# OlyBot

**OlyBot** is a Discord bot designed to provide real-time updates and reminders for the 2024 Olympic Games. This bot fetches event schedules, results, and offers personalized reminders to ensure that users never miss out on their favorite events. 

## Features

- **Event Reminders**: Set up reminders for upcoming events and receive notifications directly in Discord.
- **Live Updates**: Fetch real-time results and schedules for ongoing or upcoming Olympic events.
- **Customizable Filters**: Filter results and schedules based on country, sport, or specific events.
- **Paginated Results**: View results in an organized, paginated format, making it easy to navigate through large datasets.
- **Localization**: Times are presented according to your local timezone, ensuring you don't miss any event.

## Getting Started

### Prerequisites

Ensure you have the following installed:

- Python 3.8+
- Discord.py
- Redis
- Other dependencies listed in `requirements.txt`

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/olybot.git
   ```

2. Navigate to the project directory:

   ```bash
   cd olybot
   ```

3. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up Redis on your local machine. You can find instructions [here](https://redis.io/download).

5. Configure your bot by setting up a Discord Bot Token and adding it to your environment variables or directly into the script.

### Usage

1. Run the bot:

   ```bash
   python olybot.py
   ```

2. Add the bot to your Discord server by using the OAuth2 URL from the Discord Developer Portal.

3. Use the `!help` command in your Discord server to view available commands.

### Commands

- `!schedule [country] [sport] [event] [limit]` - Fetches the schedule for the given filters.[WILL NO LONGER WORK]
- `!results [country] [sport] [event] [limit]` - Fetches results based on the given filters.
- `!medals [country]` - Fetches medal data for the country.
- `!help` - Displays help information.

### Files

- **`olybot.py`**: The main bot script.
- **`nocList.json`**: Contains the list of National Olympic Committees (NOCs).
- **`results.json`**: Stores the fetched results from Olympic events.

### Contributing

Feel free to submit issues or pull requests if you have suggestions for improvements or new features.

### Acknowledgements

- [Discord.py](https://discordpy.readthedocs.io/)
- [Redis](https://redis.io/)
