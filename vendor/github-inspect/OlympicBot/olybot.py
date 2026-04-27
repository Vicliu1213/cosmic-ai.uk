import asyncio
from discord.ext.commands import DefaultHelpCommand
import datetime
import discord
from discord import DiscordException, app_commands
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup
from requests_html import AsyncHTMLSession
from PIL import Image, ImageDraw, ImageFont
import io
import datetime
import pytz
import redis
import urllib3
import urllib.request
import json
import countryflag
import os
import discord
from discord.ext import commands
from discord.ui import View, Button

reminders = []
REMINDER_KEY = "event_reminders"


class ReminderButton(discord.ui.Button):
    def __init__(self, custom_id, event):
        super().__init__(style=discord.ButtonStyle.primary, custom_id=custom_id, emoji="⏰")
        self.event = event

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        event_start_time = datetime.datetime.fromisoformat(
            self.event['startDate'].replace("Z", "+00:00")).astimezone(pytz.UTC)
        reminder_data = {
            "user_id": user.id,
            "event": self.event,
            "event_start_time": event_start_time.isoformat()
        }
        redis_client.rpush(REMINDER_KEY, json.dumps(reminder_data))
        await interaction.response.send_message("Reminder set!", ephemeral=True)

# Update the reminder task to trigger reminders 2 minutes before the event


@tasks.loop(seconds=60)
async def reminder_task():
    now = datetime.datetime.now(pytz.UTC)
    reminders = redis_client.lrange(REMINDER_KEY, 0, -1)
    for reminder in reminders:
        reminder = json.loads(reminder)
        event_start_time = datetime.datetime.fromisoformat(
            reminder["event_start_time"])
        reminder_time = event_start_time - datetime.timedelta(minutes=2)

        if now >= reminder_time:
            user = await bot.fetch_user(reminder["user_id"])
            embed = discord.Embed(
                title="Event Reminder",
                description=f"The event **{reminder['event']
                                           ['eventUnitName']}** is starting soon!",
                color=0x01445b
            )
            await user.send(embed=embed)
            redis_client.lrem(REMINDER_KEY, 1, json.dumps(
                reminder))  # Remove the reminder from Redis


class ReminderView(discord.ui.View):
    def __init__(self, event):
        super().__init__(timeout=None)
        self.add_item(ReminderButton(
                      custom_id="reminder_button", event=event))


class PaginatedEmbedView(View):
    def __init__(self, embeds, user, timeout=60):
        super().__init__(timeout=timeout)
        self.embeds = [embed if isinstance(
            embed, discord.Embed) else embed[0] for embed in embeds]
        self.views = [None if isinstance(
            embed, discord.Embed) else embed[1] for embed in embeds]
        self.user = user
        self.current_page = 0
        self.update_footer()

        # Add navigation buttons to the view
        self.first_button = Button(
            emoji='⏮️', style=discord.ButtonStyle.primary)
        self.first_button.callback = self.first
        self.add_item(self.first_button)

        self.prev_button = Button(
            emoji='◀️', style=discord.ButtonStyle.primary)
        self.prev_button.callback = self.previous
        self.add_item(self.prev_button)

        self.next_button = Button(
            emoji='▶️', style=discord.ButtonStyle.primary)
        self.next_button.callback = self.next
        self.add_item(self.next_button)

        self.last_button = Button(
            emoji='⏭️', style=discord.ButtonStyle.primary)
        self.last_button.callback = self.last
        self.add_item(self.last_button)

    def update_footer(self):
        for i, embed in enumerate(self.embeds):
            embed.set_footer(text=f"Page {i + 1} of {len(self.embeds)}")

    async def update_message(self, interaction):
        embed = self.embeds[self.current_page]
        view = self.views[self.current_page]

        if view:
            # If there's an additional view (like a reminder button), merge it with the navigation buttons.
            new_view = View()
            for item in view.children:
                new_view.add_item(item)
            for item in self.children:
                new_view.add_item(item)
            await interaction.response.edit_message(embed=embed, view=new_view)
        else:
            # Otherwise, just update the message with the current embed and navigation buttons.
            await interaction.response.edit_message(embed=embed, view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.user:
            # Create a new view for the interacting user
            others = discord.Embed(
                title="You cannot interact with this command. Use this personal one.", color=0xFF0000
            )
            await interaction.response.send_message(embed=others, ephemeral=True)
            new_view = PaginatedEmbedView(self.embeds, user=interaction.user)
            await interaction.followup.send(embed=self.embeds[0], view=new_view, ephemeral=True)
            return False
        return True

    async def first(self, interaction: discord.Interaction):
        self.current_page = 0
        await self.update_message(interaction)

    async def previous(self, interaction: discord.Interaction):
        self.current_page = (self.current_page - 1) % len(self.embeds)
        await self.update_message(interaction)

    async def next(self, interaction: discord.Interaction):
        # loop around:
        self.current_page = (self.current_page + 1) % len(self.embeds)
        await self.update_message(interaction)

    async def last(self, interaction: discord.Interaction):
        self.current_page = len(self.embeds) - 1
        await self.update_message(interaction)


redis_client = redis.StrictRedis(
    host='localhost', port=6379, db=0, decode_responses=True)
intents = discord.Intents.default()
intents.message_content = True
activity = discord.Game(name="Olympics 2024")
bot = commands.Bot(command_prefix='!', intents=intents, activity=activity)
# Function to fetch Astro OLY channels from the API

# File path for storing results
RESULTS_FILE = '/home/hydra/Documents/olybot/results.json'

# Initialize the results cache
if not os.path.exists(RESULTS_FILE):
    with open(RESULTS_FILE, 'w') as f:
        json.dump([], f)

# Load results from the JSON file


def load_results():
    with open(RESULTS_FILE, 'r') as f:
        return json.load(f)

# Save updated results to the JSON file


def save_results(results):
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=4)

# Fetch and update the results for finished matches of the current day


def fetch_and_update_results():
    results = load_results()
    paris_tz = pytz.timezone('Europe/Paris')
    today_date = datetime.datetime.now(paris_tz).strftime("%Y-%m-%d")

    # Fetch today's results from the API
    url = f"https://sph-s-api.olympics.com/summer/schedules/api/ENG/schedule/day/{
        today_date}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    try:
        req = requests.get(url, headers=headers)
        data = req.json()
        matches = data.get('units', [])
        for match in matches:
            status = match.get('statusDescription', '').lower()

            # Include only finished matches, with a 5-minute buffer
            if 'finished' in status:
                # Avoid duplicate entries in the cache
                if not any(m['id'] == match['id'] for m in results):
                    results.append(match)

        save_results(results)
    except Exception as e:
        print(f"Error updating results: {e}")

# Function to format and display results


def format_results(country=None, sport=None, event=None, limit=5):
    results = load_results()
    filtered_results = []
    current_time = datetime.datetime.now(pytz.UTC)
    # Load NOC list
    if sport and sport.lower() == "all":
        sport = None
    if country and country.lower() == "all":
        country = None
    if event and event.lower() == "all":
        event = None
    with open("/home/hydra/Documents/olybot/nocList.json", "r") as f:
        nocList = json.load(f)

    # Handle multiple countries separated by commas
    if country:
        country_list = {c.strip().lower() for c in country.split(',')}
    else:
        country_list = set()

    # Filter results based on criteria
    for result in results:
        if country_list:
            event_countries = {comp.get('noc', '').lower()
                               for comp in result.get('competitors', [])}
            if not country_list.issubset(event_countries):
                continue
        if sport and sport.replace(" ", "").lower() not in result['disciplineName'].replace(" ", "").lower():
            continue
        if event and event.replace(" ", "").lower() not in result['eventUnitName'].replace(" ", "").lower():
            continue

        filtered_results.append(result)

    # Sort the results by end date in descending order (most recent first)
    filtered_results.sort(key=lambda x: x['endDate'], reverse=True)

    # Get the last 'limit' results
    if limit == None:
        limit = 5
    if limit < len(filtered_results):
        filtered_results = filtered_results[:limit]

    if not filtered_results:
        error_embed = discord.Embed(
            title="No Results Found",
            description="Your query returned no results. Please check the filters and try again.",
            color=0xff0000
        )
        return [error_embed]

    results_messages = []
    for result in filtered_results:
        end_time = datetime.datetime.fromisoformat(result['endDate'].replace(
            "Z", "+00:00")).astimezone(pytz.timezone('Asia/Kolkata'))
        end_time_str = end_time.strftime('%Y-%m-%d %I:%M %p')
        time_difference = current_time - end_time
        total_seconds = int(time_difference.total_seconds())
        # 86400 seconds in a day
        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)  # 3600 seconds in an hour
        minutes = remainder // 60
        if days > 0:
            if hours > 0 or minutes > 0:
                time_remaining = f"{days} day{'s' if days >
                                              1 else ''} {hours} hr {minutes} min"
            else:
                time_remaining = f"{days} day{'s' if days > 1 else ''}"
        elif hours > 0:
            if minutes > 0:
                time_remaining = f"{hours} hr {minutes} min"
            else:
                time_remaining = f"{hours} hr"
        else:
            time_remaining = f"{minutes} min"
        embed = discord.Embed(
            title=f"{result['disciplineName']} - {result['eventUnitName']}",
            color=0x76a5be
        )

        status_description = result.get(
            'statusDescription', '').replace('Running', 'LIVE')
        detail_url = result.get('extraData', {}).get('detailUrl', '')
        if detail_url:
            status_value = f"[{
                status_description}](https://olympics.com{detail_url}) **{time_remaining}** ago"
        else:
            status_value = status_description
        status_value = "\n"+status_value
        embed.add_field(name="End Time", value=end_time_str +
                        status_value, inline=False)
        competitors = ""
        for comp in result['competitors']:
            noc = comp.get('noc', 'TBD')
            name = comp.get('name', 'TBD')
            result_info = comp.get('results', {})
            mark = result_info.get('mark', '')
            detailed_mark = result_info.get('detailedMark', [])
            position = comp.get('order', "")
            if position != "":
                position += 1
                position = str(position) + ". "
            try:
                flag = countryflag.getflag([oly_to_name(nocList, noc)])
            except:
                flag = noc

            # Check if the competitor's NOC is in the country list or if no country filter is applied
            if len(result['competitors']) <= 2:
                if mark:
                    mark = " - " + mark
                competitor_info = f"{position}{name} ({flag}){mark}"
                if detailed_mark:
                    detailed_mark_str = ' | '.join(
                        [' '.join(map(str, scores)) for scores in detailed_mark])
                    competitor_info += f" : {detailed_mark_str}"

                competitors += competitor_info + "\n"
            else:
                if not country_list or noc.lower() in country_list:
                    if mark:
                        mark = " - " + mark
                    competitor_info = f"{position}{name} ({flag}){mark}"
                    if detailed_mark:
                        detailed_mark_str = ' | '.join(
                            [' '.join(map(str, scores)) for scores in detailed_mark])
                        competitor_info += f" : {detailed_mark_str}"

                    competitors += competitor_info + "\n"

        # Handling case where competitors data exceeds embed field limit
        if len(competitors) > 1024:
            competitors = competitors.split("\n")[:10]
            competitors = "\n".join(competitors)
            competitors = "```" + competitors + "```"
            embed.add_field(name="Top 10 Competitors",
                            value=competitors, inline=False)
        else:
            competitors = "```" + competitors + "```"
            embed.add_field(name="Competitors",
                            value=competitors, inline=False)

        results_messages.append(embed)

    return results_messages


def download_image(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content))
        else:
            return None
    except Exception as e:
        print(f"Error downloading image from {url}: {e}")
        return None


def oly_to_name(nocList, code):
    for country in nocList:
        if country["id"].lower() == code.lower():
            return country["name"]


def fetch_schedule(country=None, sport=None, event=None, limit=None):
    date = datetime.datetime.today().astimezone(pytz.timezone('Europe/Paris')
                                                ).strftime("%Y-%m-%d").lower().replace(" ", "-")
    url = f"https://sph-s-api.olympics.com/summer/schedules/api/ENG/schedule/day/{
        date}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    req = urllib.request.Request(url, headers=headers)
    if sport and sport.lower() == "all":
        sport = None
    if country and country.lower() == "all":
        country = None
    if event and event.lower() == "all":
        event = None
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.load(response)
        schedule_units = data['units']
    except Exception as e:
        print(f"An error occurred: {e}")

    with open("/home/hydra/Documents/olybot/nocList.json", "r") as f:
        nocList = json.load(f)
    current_time = datetime.datetime.now(pytz.UTC)
    two_hours_later = current_time + datetime.timedelta(hours=2)

    next_5_events = []
    within_2_hours_events = []

    for event_unit in schedule_units:
        if country and not any(comp.get('noc', '').lower() == country.lower() for comp in event_unit.get('competitors', [])):
            continue
        if sport and sport.replace(" ", "").lower() not in event_unit['disciplineName'].replace(" ", "").lower():
            continue
        if event and event.replace(" ", "").lower() not in event_unit['eventUnitName'].replace(" ", "").lower():
            continue
        is_live = event_unit.get('liveFlag', False)
        event_start_time = datetime.datetime.fromisoformat(
            event_unit['startDate'].replace("Z", "+00:00")).astimezone(pytz.UTC)

        if limit is None:
            limit = 5
        if (current_time <= (event_start_time + datetime.timedelta(minutes=15)) or is_live) and len(next_5_events) < limit:
            next_5_events.append(event_unit)

        if current_time <= event_start_time <= two_hours_later:
            within_2_hours_events.append(event_unit)

    if limit:
        events_to_display = next_5_events
    elif len(within_2_hours_events) > 10:
        events_to_display = within_2_hours_events[:10]
    else:
        events_to_display = next_5_events

    schedule_messages = []

    for event in events_to_display:
        # Correct time conversion to IST
        is_live = event.get('liveFlag', False)
        event_start_time = datetime.datetime.fromisoformat(event['startDate'].replace(
            "Z", "+00:00")).astimezone(pytz.timezone('Asia/Kolkata'))
        event_start_time_str = event_start_time.strftime('%Y-%m-%d %I:%M %p')
        # say time remaining for the event to start:
        time_difference = event_start_time - current_time
        total_seconds = int(time_difference.total_seconds())
        # 86400 seconds in a day
        days, remainder = divmod(total_seconds, 86400)
        hours, remainder = divmod(remainder, 3600)  # 3600 seconds in an hour
        minutes = remainder // 60
        if days > 0:
            if hours > 0 or minutes > 0:
                time_remaining = f"{days} day{'s' if days >
                                              1 else ''} {hours} hr {minutes} min"
            else:
                time_remaining = f"{days} day{'s' if days > 1 else ''}"
        elif hours > 0:
            if minutes > 0:
                time_remaining = f"{hours} hr {minutes} min"
            else:
                time_remaining = f"{hours} hr"
        else:
            time_remaining = f"{minutes} min"
        if not is_live or current_time < event_start_time.astimezone(pytz.UTC):
            event_start_time_str += f"\n**{
                time_remaining}** remaining to start."
        embed = discord.Embed(
            title=f"{event['disciplineName']} - {event['eventUnitName']}", color=0x4a7e8d)
        if event.get('liveFlag', False):
            embed.color = 0xff0000
        embed.add_field(name="Time", value=event_start_time_str, inline=False)

        # Check if 'statusDescription' exists and replace 'Running' with 'LIVE'
        status_description = event.get(
            'statusDescription', '').replace('Running', 'LIVE')
        if status_description == '':
            status_description = "Scheduled"
        # Check if 'detailUrl' exists in 'extraData'
        detail_url = event.get('extraData', {}).get('detailUrl', '')
        if detail_url:
            status_value = f"[{
                status_description}](https://olympics.com{detail_url})"
        else:
            status_value = status_description
        embed.add_field(name="Status", value=status_value, inline=False)

        if event.get('competitors', []) != []:
            competitors = ""
            if country:
                if len(event['competitors']) > 2:
                    for comp in event['competitors']:
                        noc = comp.get('noc', 'TBD')
                        name = comp.get('name', 'TBD')
                        result = comp.get('results', {})
                        mark = result.get('mark', '')
                        detailed_mark = result.get('detailedMark', [])
                        position = comp.get('order', "")
                        if position != "":
                            position += 1
                            position = str(position)+". "
                        try:
                            flag = countryflag.getflag(
                                [oly_to_name(nocList, noc)])
                        except:
                            flag = noc

                        if comp.get('noc', '').lower() == country.lower():
                            if mark != "":
                                mark = " - " + mark
                            competitor_info = f"{position}{name} ({flag}){
                                mark}"
                            if detailed_mark:
                                detailed_mark_str = ' | '.join(
                                    [' '.join(map(str, scores)) for scores in detailed_mark])
                                competitor_info += f" : {detailed_mark_str}"

                            competitors += competitor_info + "\n"
                else:
                    for comp in event['competitors']:
                        noc = comp.get('noc', 'TBD')
                        name = comp.get('name', 'TBD')
                        result = comp.get('results', {})
                        mark = result.get('mark', '')
                        detailed_mark = result.get('detailedMark', [])
                        position = comp.get('order', "")
                        if position != "":
                            position += 1
                            position = str(position)+". "
                        try:
                            flag = countryflag.getflag(
                                [oly_to_name(nocList, noc)])
                        except:
                            flag = noc
                        if mark != "":
                            mark = " - " + mark
                        competitor_info = f"{position}{name} ({flag}){mark}"
                        if detailed_mark:
                            detailed_mark_str = ' | '.join(
                                [' '.join(map(str, scores)) for scores in detailed_mark])
                            competitor_info += f" : {detailed_mark_str}"

                        competitors += competitor_info + "\n"

            else:
                for comp in event['competitors']:
                    noc = comp.get('noc', 'TBD')
                    name = comp.get('name', 'TBD')
                    result = comp.get('results', {})
                    mark = result.get('mark', '')
                    detailed_mark = result.get('detailedMark', [])
                    position = comp.get('order', "")
                    if position != "":
                        position += 1
                        position = str(position)+". "
                    try:
                        flag = countryflag.getflag([oly_to_name(nocList, noc)])
                    except:
                        flag = noc
                    if mark != "":
                        mark = " - " + mark
                    competitor_info = f"{position}{name} ({flag}){mark}"
                    if detailed_mark:
                        detailed_mark_str = ' | '.join(
                            [' '.join(map(str, scores)) for scores in detailed_mark])
                        competitor_info += f" : {detailed_mark_str}"

                    competitors += competitor_info + "\n"
            if len(competitors) > 1024:
                competitors = competitors.split("\n")[:30]
                competitors = "\n".join(competitors)
                competitors = "```" + competitors + "```"
                embed.add_field(name="Top 30 Competitors",
                                value=competitors, inline=False)
            else:
                competitors = "```" + competitors + "```"
                embed.add_field(name="Competitors",
                                value=competitors, inline=False)

        if event_start_time > current_time:
            schedule_messages.append((embed, ReminderView(event)))
        else:
            schedule_messages.append(embed)
    if not schedule_messages:
        error_embed = discord.Embed(
            title="No Results Found",
            description="Your query returned no results. Please check the filters and try again.",
            color=0xff0000
        )
        return [error_embed]
    return schedule_messages


@bot.hybrid_command(name="table", description="Sends the current medal table")
async def table(ctx):
    await ctx.defer()
    url = 'https://en.wikipedia.org/wiki/2024_Summer_Olympics_medal_table'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    table = soup.find('table', {
                      'class': 'wikitable sortable plainrowheaders jquery-tablesorter'})
    headers = [header.text.strip() for header in table.find_all('th')]
    rows = []
    for row in table.find_all('tr')[1:]:
        cells = row.find_all(['th', 'td'])
        flag_img_tag = cells[1].find('img')
        flag_url = 'https:' + flag_img_tag['src'] if flag_img_tag else None
        row_data = [cell.text.strip() for cell in cells] + [flag_url]
        rows.append(row_data)

    headers = ["Rank", "Country", "Gold", "Silver", "Bronze", "Total"]
    country_column = [row[1] for row in rows]
    india_index = country_column.index('India')

    top_10 = rows[:9]
    india_data = rows[india_index]

    if india_data not in top_10:
        bodyp = top_10 + [india_data]
    else:
        bodyp = top_10

    font_path = '/home/hydra/Documents/olybot/font.ttf'
    font = ImageFont.truetype(font_path, 24)
    img_width = 850
    img_height = 480
    cell_height = 40
    header_height = 60
    flag_size = (30, 20)
    img = Image.new('RGB', (img_width, img_height), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    header_colors = {
        "Gold": (255, 215, 0),   # Gold color
        "Silver": (192, 192, 192),  # Silver color
        "Bronze": (205, 127, 50),  # Bronze color
        "default": (0, 0, 0)       # Default black background
    }

    y_text = 25
    x_positions = [30, 150, 450, 550, 650, 750]

    for i, header in enumerate(headers):
        bg_color = header_colors.get(header, header_colors["default"])
        draw.rectangle([x_positions[i], y_text, x_positions[i] +
                       120, y_text + cell_height - 5], fill=bg_color)
        draw.text((x_positions[i] + 10, y_text+2), header, font=font,
                  fill=(0, 0, 0) if bg_color != (0, 0, 0) else (255, 255, 255))
    draw.line((30, y_text, img_width - 30, y_text),
              fill=(255, 255, 255), width=2)
    draw.line((30, y_text + cell_height - 5, img_width - 30,
              y_text + cell_height - 5), fill=(255, 255, 255), width=2)
    for x in x_positions:
        draw.line((x, y_text, x, y_text - 10 + cell_height * 11),
                  fill=(255, 255, 255), width=2)
    draw.line((img_width - 30, y_text, img_width - 30, y_text -
              10 + cell_height * 11), fill=(255, 255, 255), width=2)

    y_text = header_height

    for row in bodyp:
        rank = row[0]
        country = row[1]
        gold = row[2]
        silver = row[3]
        bronze = row[4]
        total = row[5]
        flag_url = row[6]

        draw.text((x_positions[0]+10, y_text), rank,
                  font=font, fill=(255, 255, 255))

        if flag_url:
            flag_img = download_image(flag_url)
            if flag_img:
                flag_img.thumbnail(flag_size)
                img.paste(flag_img, (x_positions[1]+10, y_text + 10))

        country_name_x = x_positions[1] + \
            (flag_size[0] + 10 if flag_url else 0)
        draw.text((country_name_x, y_text), country,
                  font=font, fill=(255, 255, 255))
        draw.text((x_positions[2]+10, y_text), gold,
                  font=font, fill=(255, 255, 255))
        draw.text((x_positions[3]+10, y_text), silver,
                  font=font, fill=(255, 255, 255))
        draw.text((x_positions[4]+10, y_text), bronze,
                  font=font, fill=(255, 255, 255))
        draw.text((x_positions[5]+10, y_text), total,
                  font=font, fill=(255, 255, 255))

        draw.line((30, y_text + cell_height - 5, img_width - 30,
                  y_text + cell_height - 5), fill=(255, 255, 255), width=2)
        y_text += cell_height

    with io.BytesIO() as image_binary:
        img.save(image_binary, 'PNG')
        image_binary.seek(0)
        # put image in an embed:
        image = discord.File(fp=image_binary, filename='points_table.png')
        embed = discord.Embed(title="Current Standings")
        embed.set_image(url="attachment://points_table.png")
        await ctx.send(embed=embed, file=image)


@bot.hybrid_command(name="medals", description="Shows medal breakdown for a specified country.")
@app_commands.describe(country="The country (NOC code) to show the medal breakdown for.")
async def medals(ctx, country: str):
    # Defer response to allow time for processing
    if ctx.interaction:
        await ctx.interaction.response.defer(ephemeral=True)
    else:
        msg = await ctx.send("Fetching medal data...")

    medal_emoji = {
        "ME_BRONZE": "🥉",
        "ME_SILVER": "🥈",
        "ME_GOLD": "🥇"
    }

    # Scrape the data from the website
    url = 'https://olympics.com/en/paris-2024/medals'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        data = json.loads(soup.find("script", id="__NEXT_DATA__").string)

        # Extract relevant data
        medal_standings = data['props']['pageProps']['initialMedals']['medalStandings']['medalsTable']

        # Find the specific country's data
        country_data = None
        for entry in medal_standings:
            if entry['organisation'].lower() == country.lower():
                country_data = entry
                break

        if not country_data:
            # Handle case where country data is not found
            not_found_msg = f"No medal data found for the country with NOC code: {
                country.upper()}"
            if ctx.interaction:
                await ctx.interaction.followup.send(not_found_msg, ephemeral=True)
            else:
                await msg.edit(content=not_found_msg)
            return

        # Create the main embed with total medals
        total = 0
        for field in country_data['medalsNumber']:
            if field["type"] == "Total":
                total = field["total"]
        main_embed = discord.Embed(
            title=f"Medal Standings for {
                country_data['description']} ({country_data['organisation']})",
            description="",
            color=0xFFD700  # Gold color
        )
        main_embed.add_field(
            name="Ranking", value=country_data["rank"], inline=False)
        main_embed.add_field(name="Medal Count", value=total, inline=False)

        # Adding overall medal counts
        for medal in country_data['medalsNumber']:
            if medal['type'] == 'Total':
                main_embed.add_field(name="Medal Breakdown", value=f"Gold {medal_emoji['ME_GOLD']}: {medal['gold']}, Silver {medal_emoji['ME_SILVER']}: {
                                     medal['silver']}, Bronze {medal_emoji['ME_BRONZE']}: {medal['bronze']}, Total: {medal['total']}", inline=False)

        main_embed.set_footer(text=f"Data last updated: {
                              data['props']['pageProps']['generatedAt']}")

        # Gender breakdown embed
        gender_embed = discord.Embed(
            title=f"Medal Breakdown for {
                country_data['description']} ({country_data['organisation']}) by Gender",
            color=0x1F8B4C  # Different color for gender breakdown
        )
        gender_breakdown = {medal['type']: medal for medal in country_data['medalsNumber'] if medal['type'] in [
            'Men', 'Women', 'Mixed']}
        for gender, medal in gender_breakdown.items():
            gender_embed.add_field(name=f"{gender} Medals", value=f"Gold {medal_emoji['ME_GOLD']}: {medal['gold']}, Silver {medal_emoji['ME_SILVER']}: {
                                   medal['silver']}, Bronze {medal_emoji['ME_BRONZE']}: {medal['bronze']}, Total: {medal['total']}", inline=False)

        # Prepare embeds for disciplines and medalists
        discipline_embeds = []
        current_embed = None
        field_count = 0
        max_fields_per_embed = 5  # Set a limit to avoid hitting the field limit per embed
        max_chars_per_field = 1024  # Discord's character limit per field value

        for discipline in country_data['disciplines']:
            discipline_info = ""
            medalists = []

            for medal_winner in discipline['medalWinners']:
                medal_type = medal_winner['medalType']
                medalists.append(f"**{medal_winner['competitorDisplayName']}** in {
                                 medal_winner['eventDescription']}: **{medal_type.replace('ME_', '')} {medal_emoji[medal_type]}**")

            # Join medalists into a string and split at natural boundaries
            medalists_str = "\n".join(medalists)

            # Split into chunks without breaking formatting
            parts = []
            while len(medalists_str) > max_chars_per_field:
                # Find the last newline character within the limit
                last_nl = medalists_str.rfind('\n', 0, max_chars_per_field)
                if last_nl == -1:
                    # No newline character found, force split
                    parts.append(medalists_str[:max_chars_per_field])
                    medalists_str = medalists_str[max_chars_per_field:]
                else:
                    # Split at the last newline
                    parts.append(medalists_str[:last_nl])
                    medalists_str = medalists_str[last_nl + 1:]

            # Add the last remaining part
            if medalists_str:
                parts.append(medalists_str)

            # Create embeds for each part
            for part_index, part in enumerate(parts):
                if current_embed is None or field_count >= max_fields_per_embed:
                    if current_embed is not None:
                        discipline_embeds.append(current_embed)
                    current_embed = discord.Embed(
                        title=f"Medal Breakdown for {
                            country_data['description']} ({country_data['organisation']}) by Sport",
                        color=0xFFD700  # Gold color
                    )
                    field_count = 0

                # Add the discipline info to the current embed
                field_name = f"{discipline['name']}" if part_index == 0 else f"{
                    discipline['name']} (continued)"
                current_embed.add_field(
                    name=field_name, value=part, inline=False)
                field_count += 1

        # Add the last embed if it exists
        if current_embed is not None:
            discipline_embeds.append(current_embed)

        # Send the main embed first
        embeds = [main_embed, gender_embed] + discipline_embeds
        view = PaginatedEmbedView(embeds, user=ctx.author)

        if ctx.interaction:
            await ctx.interaction.followup.send(embed=embeds[0], view=view, ephemeral=True)
        else:
            await msg.edit(content="", embed=embeds[0], view=view)

    except Exception as e:
        error_msg = f"An error occurred while fetching the medal data: {e}"
        if ctx.interaction:
            await ctx.interaction.followup.send(error_msg, ephemeral=True)
        else:
            await msg.edit(content=error_msg)


@bot.hybrid_command(name="schedule", description="Shows schedule of upcoming matches.")
@app_commands.describe(country="Filters by NOC, enter the IOC Code", sport="Filters by sport", event="Filter by event", limit="Number of events to display")
async def schedule(ctx, country: str = None, sport: str = None, event: str = None, limit: int = 5):
    is_interaction = hasattr(ctx, 'interaction') and ctx.interaction

    if is_interaction:
        await ctx.interaction.response.defer(ephemeral=True)
    else:
        embed = discord.Embed(
            title="Fetching schedule", description="", color=0x01445b
        )
        msg = await ctx.send(embed=embed)

    schedule_messages = fetch_schedule(country, sport, event, limit)

    # Check if the first message is a tuple (future event)
    if isinstance(schedule_messages[0], tuple):
        first_embed, first_view = schedule_messages[0]
    else:
        first_embed = schedule_messages[0]
        first_view = None

    # Combine the reminder view with the pagination view if needed
    if first_view:
        view = discord.ui.View()
        # Add the reminder button
        for item in first_view.children:
            view.add_item(item)
        # Add the pagination buttons
        paginated_view = PaginatedEmbedView(schedule_messages, user=ctx.author)
        for item in paginated_view.children:
            view.add_item(item)
    else:
        view = PaginatedEmbedView(schedule_messages, user=ctx.author)

    if is_interaction:
        await ctx.interaction.followup.send(embed=first_embed, view=view, ephemeral=True)
    else:
        await msg.edit(embed=first_embed, view=view)


class StopButton(Button):
    def __init__(self, message, user):
        super().__init__(label="Stop", style=discord.ButtonStyle.danger)
        self.message = message
        self.user = user

    async def callback(self, interaction: discord.Interaction):
        # Check if the user is an admin
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You don't have permission to stop this.", ephemeral=True)
            return

        # Stop the task and disable the button
        self.view.stop()  # Stop the View's loop
        await self.message.edit(content="**Live scorecard updates stopped.**", embed=None, view=None)
        # Acknowledge the interaction without sending a response
        await interaction.response.defer()


class ScorecardView(View):
    def __init__(self, message, user, timeout=None):
        super().__init__(timeout=timeout)
        self.message = message
        self.user = user
        self.add_item(StopButton(message=message, user=user))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Ensure only the command invoker or admins can interact with the buttons
        if interaction.user.guild_permissions.administrator or interaction.user == self.user:
            return True
        await interaction.response.send_message("You don't have permission to use this.", ephemeral=True)
        return False


@bot.hybrid_command(name="scorecard", description="Shows the live scorecard of a match based on filters.")
@app_commands.describe(country="Filters by NOC, enter the IOC Code", sport="Filters by sport", event="Filter by event")
async def scorecard(ctx, country: str = None, sport: str = None, event: str = None):
    # Check if the user is an admin
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You don't have permission to run this command.", ephemeral=True)
        return

    # Determine if the command was invoked as an interaction (slash command) or as a text command
    is_interaction = hasattr(ctx, 'interaction') and ctx.interaction

    # Defer the response for slash commands
    if is_interaction:
        await ctx.interaction.response.defer(ephemeral=True)
    else:
        # For regular text commands, send an initial message
        embed = discord.Embed(
            title="Fetching live scorecard", description="", color=0x01445b
        )
        msg = await ctx.send(embed=embed)

    # Fetch the schedule
    schedule_messages = fetch_schedule(country, sport, event, limit=1)
    print(schedule_messages)

    # Find the first live event
    live_event = None
    for msgs in schedule_messages:
        if 'LIVE' in msgs.fields[1].value:
            live_event = msgs
            break

    if live_event is None:
        error_embed = discord.Embed(
            title="No Live Event Found",
            description="There are no live events currently available for the given filters.",
            color=0xff0000
        )
        if is_interaction:
            await ctx.interaction.followup.send(embed=error_embed, ephemeral=True)
        else:
            await msg.edit(embed=error_embed)
        return

    live_embed = live_event

    if is_interaction:
        scorecard_msg = await ctx.interaction.followup.send(embed=live_embed, ephemeral=False)
    else:
        scorecard_msg = await msg.edit(embed=live_embed)

    view = ScorecardView(message=scorecard_msg, user=ctx.author)
    await scorecard_msg.edit(view=view)

    # Update the scorecard every 2 minutes
    while not view.is_finished():
        await asyncio.sleep(45)  # Wait for 2 minutes

        # Fetch the latest schedule to get updated information
        updated_schedule_messages = fetch_schedule(country, sport, event)

        # Find the updated information for the same live event
        updated_live_event = None
        for msg in updated_schedule_messages:
            if 'LIVE' in msg.fields[1].value:
                updated_live_event = msg
                break

        if updated_live_event is None:
            # If the event is no longer live, stop updating
            end_embed = discord.Embed(
                title="Live Event Ended",
                description="The live event has ended or is no longer available.",
                color=0xff0000
            )
            await scorecard_msg.edit(embed=end_embed, view=None)
            break

        updated_live_embed = updated_live_event
        await scorecard_msg.edit(embed=updated_live_embed, view=view)


@bot.hybrid_command(name="results", description="Shows results of finished matches.")
@app_commands.describe(country="Filters by NOC, enter the IOC Code", sport="Filters by sport", event="Filters by event", limit="Number of events to display")
async def results(ctx, country: str = None, sport: str = None, event: str = None, limit: int = 5):
    # Determine if the command was invoked as an interaction (slash command) or as a text command
    is_interaction = hasattr(ctx, 'interaction') and ctx.interaction

    # Defer the response for slash commands
    if is_interaction:
        await ctx.interaction.response.defer(ephemeral=True)
    else:
        # For regular text commands, send an initial message
        embed = discord.Embed(
            title="Fetching results", description="", color=0x01445b
        )
        msg = await ctx.send(embed=embed)

    # Update and fetch results
    fetch_and_update_results()
    results_messages = format_results(country, sport, event, limit)

    # Create a PaginatedEmbedView with the results
    view = PaginatedEmbedView(results_messages, user=ctx.author)

    # Send the initial embed with buttons
    if is_interaction:
        await ctx.interaction.followup.send(embed=results_messages[0], view=view, ephemeral=True)
    else:
        await msg.edit(embed=results_messages[0], view=view)


class CustomHelpCommand(DefaultHelpCommand):
    def __init__(self, **options):
        super().__init__(**options)

    async def send_bot_help(self, mapping):
        """Send the help message for the bot."""
        ctx = self.context
        help_embed = discord.Embed(
            title="🤖 Olympics Bot Help",
            description="Welcome to the **Olympics Bot**! Below you can find detailed information about the available commands.",
            color=0x1F8B4C  # A distinct color for the help embed
        )

        help_embed.add_field(
            name="📅 **/schedule**",
            value=(
                "Displays the schedule of upcoming matches with optional filters.\n\n"
                "**Parameters:**\n"
                "- `country` (optional): Filter by NOC (National Olympic Committee) code. Use the IOC code (e.g., `USA`, `IND`).\n"
                "- `sport` (optional): Filter by sport name (e.g., `Basketball`, `Swimming`).\n"
                "- `event` (optional): Filter by event name (e.g., `100m Freestyle`, `Gold Medal Match`).\n"
                "- `limit` (optional): Specify the number of events to display (default is 5).\n\n"
                "**Example Usage:**\n"
                "- `/schedule country:USA sport:Athletics event:Javelin limit:3`\n"
                "- `/schedule` (shows all upcoming events)\n"
                "- `!schedule IND badminton bronze 1` for text command\n"
                "- `!schedule all boxing all 1`(use the keyword `all` if you dont want to filter)"
            ),
            inline=False
        )

        help_embed.add_field(
            name="🥇 **/medals**",
            value=(
                "Displays the medal breakdown for a specified country.\n\n"
                "**Parameters:**\n"
                "- `country`: The NOC (National Olympic Committee) code of the country to display (e.g., `USA`, `IND`).\n\n"
                "**Example Usage:**\n"
                "- `/medals country:USA`\n"
                "- `!medals IND`"
            ),
            inline=False
        )

        help_embed.add_field(
            name="📊 **/table**",
            value=(
                "Displays the current medal table.\n\n"
                "**Example Usage:**\n"
                "- `/table`\n"
                "- `!table`"
            ),
            inline=False
        )

        help_embed.set_footer(
            text="Olympics Bot - Bringing you live updates and information on the Paris 2024 Olympics!"
        )

        await ctx.send(embed=help_embed)


# Set the custom help command
bot.help_command = CustomHelpCommand()

# Background task to check and send reminders


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.tree.sync()
    reminder_task.start()
bot.run(os.getenv('TOKEN'))
