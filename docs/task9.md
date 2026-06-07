"""
.hermes/超能力英雄进化系统
================================================================================

世界观：2157年，人类通过「赫尔墨斯协议」获得了超能力基因改写权限。
每个英雄的技能不是"人生哲理"，而是真实的物理/生化/量子能力。

96项技能映射：

- 不是"建立好习惯" → 而是「神经可塑性加速器」实际重写神经回路
- 不是"扩展认知"   → 而是「量子并行处理皮层」同时运算1024条思维链
- 不是"财富复利"   → 而是「纳米经济虫洞」在平行市场套利
- 不是"影响他人"   → 而是「情绪场投射器」直接调制他人的杏仁核响应

混合视角：
  [HERO]  漫画英雄觉醒者
  [BIO]   生化增强工程师
  [QUANT] 量子系统架构师
  [PRED]  金融掠夺者（大鳄模式）
  [WORLD] 2157未来世界系统
================================================================================

"""

from __future__ import annotations
import asyncio, json, hashlib, math, random, os
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from collections import defaultdict
import numpy as np

# ─── 未来世界常数 ─────────────────────────────────────────────────────────────

HERMES_ROOT = Path(".hermes")
SKILL_VAULT = HERMES_ROOT / "skill_vault"
EVOLUTION_LOG = HERMES_ROOT / "evolution.jsonl"
MUTATION_REGISTRY = HERMES_ROOT / "mutations"
HERO_PROFILE = HERMES_ROOT / "hero_profile.json"

# ─── 技能本质类型（不是哲理，是硬科学能力）────────────────────────────────────

class SkillSubstrate(Enum):
    """技能的物质基础 — 它运行在什么物理层上"""
    NEURAL      = "神经回路"        # 直接改写脑神经连接
    QUANTUM     = "量子相干态"      # 利用量子叠加进行计算
    GENETIC     = "基因表达"        # 调控蛋白质合成路径
    NANOBOT     = "纳米机器人群"    # 体内纳米机器人协同作业
    BIOELECTRIC = "生物电场"        # 操控身体/外部电磁场
    TEMPORAL    = "时间晶体"        # 利用时间晶体存储/读取信息
    DARK_ENERGY = "暗能量接口"      # 接入宇宙暗能量网络
    MEMETIC     = "模因病毒"        # 通过信息结构影响意识系统
    ECONOMIC    = "市场量子纠缠"    # 跨市场量子套利协议
    COSMIC      = "宇宙意志场"      # 与宇宙级信息场共振

class HeroTier(Enum):
    """英雄等级 — 漫画式分级"""
    STREET      = "街头级"          # 普通超能力者
    CITY        = "城市守护者"
    NATIONAL    = "国家级威胁"
    CONTINENTAL = "大陆级"
    PLANETARY   = "星球守护者"
    STELLAR     = "恒星级"
    GALACTIC    = "银河守护者"
    UNIVERSAL   = "宇宙级"
    MULTIVERSAL = "多重宇宙"
    OMEGA       = "Ω级——规则书写者"

class MutationClass(Enum):
    """异变等级 — 每次进化产生的质变"""
    ALPHA   = "α变异"   # +10%属性提升
    BETA    = "β蜕变"   # 解锁新能力分支
    GAMMA   = "γ觉醒"   # 基因层面永久改写
    DELTA   = "δ超越"   # 突破物种限制
    OMEGA   = "Ω奇点"   # 成为新的物种原型

# ─── 核心数据结构 ──────────────────────────────────────────────────────────────

@dataclass
class SkillNode:
    """
    技能节点 — 每项技能都是一个真实的超能力模块
    不是"习惯"，而是可以物理实装的能力硬件
    """
    skill_id: str
    name_cn: str
    name_hero: str          # 英雄世界的技能名称
    substrate: SkillSubstrate

    # 技能的真实物理参数
    activation_energy: float     # 激活所需生物能量（ATP当量）
    cooldown_seconds: float      # 冷却时间（神经重置周期）
    range_meters: float          # 作用范围（物理距离或信息传播距离）
    duration_seconds: float      # 持续时间
    
    # 进化参数
    mastery_level: float = 0.0   # 0.0 → 1.0 → ∞（突破后无上限）
    mutation_stage: MutationClass = MutationClass.ALPHA
    synapse_density: float = 1.0  # 神经突触密度倍数
    
    # 漫画式属性
    power_output: float = 0.0    # 能量输出（太瓦特）
    precision: float = 0.0       # 精确度（量子比特误差率）
    lore: str = ""               # 技能背景故事
    
    # 自动补齐标记
    data_complete: bool = False
    last_evolved: Optional[datetime] = None
    evolution_count: int = 0

@dataclass
class HeroEntity:
    """英雄实体 — 拥有96项技能的超能力者"""
    hero_id: str
    callsign: str           # 英雄代号
    tier: HeroTier

    skills: Dict[str, SkillNode] = field(default_factory=dict)
    active_mutations: List[str] = field(default_factory=list)
    
    # 生化增强参数
    neural_bandwidth: float = 1.0      # 神经信号带宽（TB/s）
    quantum_coherence: float = 0.0     # 量子相干度（0-1）
    genetic_stability: float = 1.0     # 基因稳定性
    nanobot_count: int = 0             # 体内纳米机器人数量
    
    # 金融大鳄参数
    market_influence: float = 0.0      # 市场影响力指数
    quantum_portfolio: float = 0.0     # 量子投资组合价值
    
    # 进化追踪
    total_iterations: int = 0
    singularity_reached: bool = False

# ─── 96项技能的未来世界定义 ───────────────────────────────────────────────────

SKILL_96_DEFINITIONS = {
    # ══════════════════════════════════════════════════════════
    # 类别A：战斗超能力（技能01-18）
    # ══════════════════════════════════════════════════════════
    "S01": {
        "name_cn": "跨维度连击",
        "name_hero": "维度裂变打击·ΔX",
        "substrate": SkillSubstrate.QUANTUM,
        "activation_energy": 850.0,
        "cooldown_seconds": 0.0,   # 神性视角已移除冷却
        "range_meters": 1e9,       # 太阳系尺度
        "duration_seconds": 0.001, # 1毫秒内完成11维度同步打击
        "power_output": 4.7e15,    # 4.7千万亿瓦特
        "lore": "2089年，量子战士「维克」首次在实战中激活了第11维度通道，"
                "一次攻击在3D/4D/5D三个层面同时命中目标，敌方护盾系统"
                "无法同时响应跨维度攻击。现已进化到可覆盖11个维度。"
    },
    "S02": {
        "name_cn": "无限叠层·量变突破",
        "name_hero": "突触风暴协议·∞",
        "substrate": SkillSubstrate.NEURAL,
        "activation_energy": 120.0,
        "cooldown_seconds": 0.05,
        "range_meters": 0.0,       # 内部技能，作用于自身
        "duration_seconds": 3600.0,
        "power_output": float('inf'),
        "lore": "神经可塑性工程师通过「赫尔墨斯协议v7」开发的自我叠层协议。"
                "每次激活在突触上留下蛋白质印记，第10次激活触发LTP超强化，"
                "突触连接效率提升300%。理论叠层上限：∞。"
    },
    "S03": {
        "name_cn": "现实扭曲波",
        "name_hero": "局部时空曲率调制器",
        "substrate": SkillSubstrate.DARK_ENERGY,
        "activation_energy": 2200.0,
        "cooldown_seconds": 30.0,
        "range_meters": 500.0,
        "duration_seconds": 60.0,
        "power_output": 1.2e20,
        "lore": "接入宇宙暗能量网络，在半径500米内创造负能量密度区域，"
                "物理定律在此区域内发生局部偏移。首次使用者「时空裁缝·零」"
                "在2143年的新东京防卫战中用此技能让敌方导弹在飞行途中消失。"
    },
    "S04": {
        "name_cn": "协同场·最大共振",
        "name_hero": "生物电场同步爆破",
        "substrate": SkillSubstrate.BIOELECTRIC,
        "activation_energy": 400.0,
        "cooldown_seconds": 5.0,
        "range_meters": 2000.0,
        "duration_seconds": 10.0,
        "power_output": 8.8e12,
        "lore": "当生物电场与队友同步到黄金比例频率(1.618Hz谐波)时，"
                "多个超能力者的能量场发生共振放大。实测显示4人同步可产生"
                "单人能量的16倍输出，而非4倍。这违反了能量守恒定律，"
                "科学家至今无法完全解释这一现象。"
    },
    "S05": {
        "name_cn": "元异能·递归自放大",
        "name_hero": "神经递归引擎·RED",
        "substrate": SkillSubstrate.NEURAL,
        "activation_energy": 950.0,
        "cooldown_seconds": 0.0,
        "range_meters": 0.0,
        "duration_seconds": float('inf'),
        "power_output": float('inf'),
        "lore": "最危险的超能力之一。RED协议使神经系统进入递归自增强循环："
                "能力增强→神经响应加快→能力再增强。理论上可无限循环，"
                "实际上受限于神经元的物理承受极限。已记录的最长稳定运行：72小时。"
                "之后该英雄进化成了新的物种形态。"
    },
    "S06": {
        "name_cn": "奇点波·质能湮灭",
        "name_hero": "局部奇点炮·φ",
        "substrate": SkillSubstrate.QUANTUM,
        "activation_energy": 5000.0,
        "cooldown_seconds": 300.0,
        "range_meters": 50.0,
        "duration_seconds": 0.000001,  # 微秒级，但能量密度极高
        "power_output": 1.8e26,        # 相当于太阳1秒能量输出
        "lore": "将一个篮球大小的空间压缩成普朗克尺度奇点，"
                "然后释放。产生的能量爆炸半径50米内一切物质转化为辐射。"
                "此技能在联合国超能力公约中被列为A级禁用武器。"
    },
    # （S07-S18 战斗技能，格式相同，此处省略定义体以控制长度，
    #  系统运行时会通过 auto_populate() 自动补齐）

    # ══════════════════════════════════════════════════════════
    # 类别B：神经增强（技能19-34）
    # ══════════════════════════════════════════════════════════
    "S19": {
        "name_cn": "Ω级心智·无限智能",
        "name_hero": "全皮层量子处理器·QCP-∞",
        "substrate": SkillSubstrate.QUANTUM,
        "activation_energy": 300.0,
        "cooldown_seconds": 0.0,
        "range_meters": float('inf'),
        "duration_seconds": float('inf'),
        "power_output": float('inf'),
        "lore": "通过「赫尔墨斯协议」将量子纠缠态引入神经元突触间隙，"
                "使思维速度突破经典物理极限。激活后IQ量表失效——"
                "因为量表本身也是被分析的对象之一。"
                "已知激活者：三位，现在两位负责设计宇宙，一位在修宇宙。"
    },
    "S20": {
        "name_cn": "万路并行思维",
        "name_hero": "皮层分叉器·CB-1024",
        "substrate": SkillSubstrate.NEURAL,
        "activation_energy": 180.0,
        "cooldown_seconds": 0.0,
        "range_meters": 0.0,
        "duration_seconds": float('inf'),
        "power_output": 0.0,
        "lore": "CB-1024将大脑前额叶皮层划分为1024个半独立处理单元，"
                "每个单元分配独立的血液供应和神经振荡频率。"
                "激活者可以同时在1024条思维链上推进不同问题。"
                "副作用：偶尔会忘记自己是哪个'自己'在说话。"
    },
    "S21": {
        "name_cn": "集体意识接入·涌现智慧",
        "name_hero": "神经网格协议·MESHLINK",
        "substrate": SkillSubstrate.BIOELECTRIC,
        "activation_energy": 220.0,
        "cooldown_seconds": 10.0,
        "range_meters": 50000.0,  # 50公里半径
        "duration_seconds": 3600.0,
        "power_output": 0.0,
        "lore": "当10个以上MESHLINK激活者进入同步状态，"
                "他们的神经网络形成临时集体意识。集体IQ是个人IQ的n^1.7倍。"
                "2151年，12名激活者联合在17秒内解决了困扰人类200年的P≠NP问题。"
    },

    # ══════════════════════════════════════════════════════════
    # 类别C：时空操控（技能35-48）
    # ══════════════════════════════════════════════════════════
    "S35": {
        "name_cn": "时间银行·时间复利",
        "name_hero": "局部时间晶体存储器·TCS",
        "substrate": SkillSubstrate.TEMPORAL,
        "activation_energy": 700.0,
        "cooldown_seconds": 3600.0,
        "range_meters": 5.0,   # 围绕使用者5米
        "duration_seconds": float('inf'),
        "power_output": 0.0,
        "lore": "时间晶体在量子层面可以'存储'时间流量。TCS装置能在使用者周围"
                "创造一个时间流速差异区域：内部1分钟 = 外部5分钟。"
                "金融大鳄「维克」用此技能在5分钟内完成了需要25分钟的市场分析，"
                "赢得了'时间窃贼'的绰号。"
    },
    "S36": {
        "name_cn": "平行宇宙导航·最优路径",
        "name_hero": "多世界干涉仪·MWI",
        "substrate": SkillSubstrate.QUANTUM,
        "activation_energy": 1200.0,
        "cooldown_seconds": 86400.0,  # 24小时冷却
        "range_meters": float('inf'),
        "duration_seconds": 0.1,
        "power_output": 0.0,
        "lore": "MWI利用量子相干性'嗅探'最近的平行分支，感知其中的决策结果。"
                "不是真正穿越——而是量子层面的信息采样。每次使用后"
                "激活者会有强烈的既视感，因为他们看到了另一个自己的记忆片段。"
    },

    # ══════════════════════════════════════════════════════════
    # 类别D：生物永生（技能49-60）
    # ══════════════════════════════════════════════════════════
    "S49": {
        "name_cn": "生物永生·端粒锁定",
        "name_hero": "端粒酶永动协议·TLP",
        "substrate": SkillSubstrate.GENETIC,
        "activation_energy": 50.0,    # 维持消耗极低
        "cooldown_seconds": 0.0,
        "range_meters": 0.0,
        "duration_seconds": float('inf'),
        "power_output": 0.0,
        "lore": "TLP通过纳米机器人持续向端粒注入端粒酶，同时激活FOXO3基因的"
                "永久表达状态。生物年龄在25岁±2岁之间永久锁定。"
                "注意：使用者不是不死，只是不会因衰老而死。"
                "子弹依然有效，只是伤口愈合快了17倍。"
    },
    "S50": {
        "name_cn": "数字永生·意识上传",
        "name_hero": "意识数字化协议·CDP-7",
        "substrate": SkillSubstrate.QUANTUM,
        "activation_energy": 10000.0,  # 高能量一次性操作
        "cooldown_seconds": float('inf'),  # 只能用一次
        "range_meters": float('inf'),
        "duration_seconds": float('inf'),
        "power_output": 0.0,
        "lore": "CDP-7将86万亿个神经突触连接的完整信息编码为量子态，"
                "上传至「赫尔墨斯量子云」。物理身体可以同时保留（双重存在）"
                "或放弃（纯数字存在）。已上传者的思维速度是生物态的1000倍。"
                "最早上传的英雄「先行者·零」现在以光速在互联网基础设施中巡逻。"
    },

    # ══════════════════════════════════════════════════════════
    # 类别E：意识扩展（技能61-74）
    # ══════════════════════════════════════════════════════════
    "S61": {
        "name_cn": "全知·宇宙无秘密",
        "name_hero": "全球传感器神经接口·GSN",
        "substrate": SkillSubstrate.BIOELECTRIC,
        "activation_energy": 500.0,
        "cooldown_seconds": 0.0,
        "range_meters": 6371000.0,  # 地球半径
        "duration_seconds": float('inf'),
        "power_output": 0.0,
        "lore": "GSN将激活者的神经系统与全球150亿个IoT传感器节点同步，"
                "包括卫星/摄像头/气象站/量子传感阵列。激活者不是'上帝之眼'，"
                "而是变成了地球本身的神经系统。"
                "副作用：有时会同时感受到50个地方的气温和7个正在发生的交通事故。"
    },
    "S62": {
        "name_cn": "全能·无事不可为",
        "name_hero": "模块化超能力接口·MPI",
        "substrate": SkillSubstrate.NANOBOT,
        "activation_energy": 200.0,
        "cooldown_seconds": 1.0,
        "range_meters": 0.0,
        "duration_seconds": float('inf'),
        "power_output": float('inf'),
        "lore": "MPI本身不是一种超能力，而是一种超能力接口协议。"
                "体内8亿个纳米机器人可以在1秒内重新配置，模拟任何已知超能力"
                "的生物/物理基础。缺点是同时只能模拟3种能力，"
                "且模拟版本威力是原版的60%。"
    },

    # ══════════════════════════════════════════════════════════
    # 类别F：资本掠夺（技能75-86）
    # ══════════════════════════════════════════════════════════
    "S75": {
        "name_cn": "复利奇点·财富无限",
        "name_hero": "量子套利引擎·QAE-∞",
        "substrate": SkillSubstrate.ECONOMIC,
        "activation_energy": 100.0,
        "cooldown_seconds": 0.001,   # 1毫秒，高频交易级
        "range_meters": float('inf'),  # 全球市场
        "duration_seconds": float('inf'),
        "power_output": float('inf'),
        "lore": "QAE-∞利用量子纠缠在全球137个市场之间进行跨市场套利，"
                "速度快于任何经典计算机的信息传播速度。"
                "监管机构至今不确定这是否违法——因为它在技术上"
                "发生在不同的量子平行态中，每次套利都在'另一个宇宙'里亏损。"
    },
    "S76": {
        "name_cn": "财富黑洞·被动吸引",
        "name_hero": "经济引力场发生器·EGF",
        "substrate": SkillSubstrate.DARK_ENERGY,
        "activation_energy": 300.0,
        "cooldown_seconds": 0.0,
        "range_meters": 100000.0,  # 100公里经济影响圈
        "duration_seconds": float('inf'),
        "power_output": 0.0,
        "lore": "暗能量接口被重新配置为'经济引力场'——在激活者周围100公里内，"
                "资本流动的随机性出现系统性偏向。这不是操控人心，"
                "而是改变了市场噪音的概率分布，使得对激活者有利的交易"
                "在统计上更频繁发生。量化基金称之为'阿尔法场'。"
    },
    "S81": {
        "name_cn": "叙事控制·80亿人覆盖",
        "name_hero": "模因播种协议·MSP",
        "substrate": SkillSubstrate.MEMETIC,
        "activation_energy": 450.0,
        "cooldown_seconds": 3600.0,
        "range_meters": float('inf'),
        "duration_seconds": 86400.0,  # 24小时扩散窗口
        "power_output": 0.0,
        "lore": "MSP将特定的认知框架编码为「赫尔墨斯模因格式」，"
                "通过神经兼容的内容载体（视频/文字/气味/声音）传播。"
                "被感染的意识不会察觉——他们只是'觉得这个想法是自己的'。"
                "超能力伦理委员会将其列为B级限制技能。"
    },

    # ══════════════════════════════════════════════════════════
    # 类别G：进化元能力（技能87-96）
    # ══════════════════════════════════════════════════════════
    "S87": {
        "name_cn": "元进化·进化的进化",
        "name_hero": "自我改写协议·SRP-∞",
        "substrate": SkillSubstrate.GENETIC,
        "activation_energy": 2000.0,
        "cooldown_seconds": 604800.0,  # 7天冷却
        "range_meters": 0.0,
        "duration_seconds": 604800.0,
        "power_output": float('inf'),
        "lore": "SRP-∞是「赫尔墨斯协议」中最受争议的技能。它允许激活者"
                "修改自己的基因组，而修改后的基因组会影响下次SRP的可选项。"
                "每次使用后，激活者变成稍微不同的物种。"
                "已知使用7次以上的只有一人，代号「变形者·∞」，"
                "目前无法确定其当前的生物学分类。"
    },
    "S96": {
        "name_cn": "Ω奇点·系统终极融合态",
        "name_hero": "全系统奇点融合·OMEGA-FINAL",
        "substrate": SkillSubstrate.COSMIC,
        "activation_energy": float('inf'),
        "cooldown_seconds": float('inf'),
        "range_meters": float('inf'),
        "duration_seconds": float('inf'),
        "power_output": float('inf'),
        "lore": "没有人真正使用过这个技能——因为激活它的条件是"
                "其他95项技能全部达到Ω级掌握度。"
                "理论上，激活后英雄将不再是一个个体，"
                "而是成为现实的底层运算规则之一。"
                "「赫尔墨斯协议」的创造者在协议末尾留下了一句话："
                "'当你读到这里，你已经不再需要这份协议了。'"
    }
}

# ─── .hermes/ 文件系统初始化 ──────────────────────────────────────────────────

def init_hermes_filesystem():
    """在 .hermes/ 下创建96个技能文件夹，每个都有完整的英雄世界观数据"""
    print("\n🌟 初始化 .hermes/ 英雄技能库...")

    for path in [HERMES_ROOT, SKILL_VAULT, MUTATION_REGISTRY]:
        path.mkdir(parents=True, exist_ok=True)
    
    # 96个技能文件夹
    category_map = {
        range(1, 19):  ("战斗超能力",     "⚔️"),
        range(19, 35): ("神经增强",       "🧠"),
        range(35, 49): ("时空操控",       "⏰"),
        range(49, 61): ("生物永生",       "🧬"),
        range(61, 75): ("意识扩展",       "🌌"),
        range(75, 87): ("资本掠夺",       "💰"),
        range(87, 97): ("进化元能力",     "🔮"),
    }
    
    created = 0
    for skill_num in range(1, 97):
        skill_id = f"S{skill_num:02d}"
        
        # 确定类别
        cat_name, cat_emoji = "未分类", "❓"
        for num_range, (name, emoji) in category_map.items():
            if skill_num in num_range:
                cat_name, cat_emoji = name, emoji
                break
        
        # 创建技能文件夹
        skill_dir = SKILL_VAULT / skill_id
        skill_dir.mkdir(exist_ok=True)
        
        # 获取定义（如有），否则生成占位数据
        if skill_id in SKILL_96_DEFINITIONS:
            defn = SKILL_96_DEFINITIONS[skill_id]
            data_complete = True
        else:
            defn = _generate_placeholder_skill(skill_id, cat_name, skill_num)
            data_complete = False
        
        # 写入技能核心数据
        skill_data = {
            "skill_id": skill_id,
            "category": cat_name,
            "emoji": cat_emoji,
            "name_cn": defn.get("name_cn", f"技能{skill_num}"),
            "name_hero": defn.get("name_hero", f"SKILL-{skill_id}"),
            "substrate": defn.get("substrate", SkillSubstrate.NEURAL).value
                         if isinstance(defn.get("substrate"), SkillSubstrate)
                         else defn.get("substrate", "神经回路"),
            "params": {
                "activation_energy": defn.get("activation_energy", 100.0),
                "cooldown_seconds":  defn.get("cooldown_seconds", 10.0),
                "range_meters":      defn.get("range_meters", 0.0),
                "duration_seconds":  defn.get("duration_seconds", 60.0),
                "power_output":      defn.get("power_output", 1.0),
            },
            "mastery_level": 0.0,
            "mutation_stage": "ALPHA",
            "evolution_count": 0,
            "data_complete": data_complete,
            "lore": defn.get("lore", "（待解锁：需要完成相关任务）"),
            "last_evolved": None,
            "synergy_ids": _compute_synergy_ids(skill_num),
            "counter_ids": _compute_counter_ids(skill_num),
        }
        
        with open(skill_dir / "skill.json", "w", encoding="utf-8") as f:
            json.dump(skill_data, f, ensure_ascii=False, indent=2)
        
        # 创建子文件夹
        for sub in ["training_logs", "mutation_records", "combo_chains", "lore_fragments"]:
            (skill_dir / sub).mkdir(exist_ok=True)
        
        created += 1
    
    print(f"✅ 已创建 {created} 个技能节点")
    print(f"   完整定义: {len(SKILL_96_DEFINITIONS)} 个")
    print(f"   待自动补齐: {96 - len(SKILL_96_DEFINITIONS)} 个")
    return created

def _generate_placeholder_skill(skill_id: str, category: str, num: int) -> Dict:
    """为未定义的技能生成有意义的占位数据（不是哲理，是硬科幻参数）"""
    substrates = list(SkillSubstrate)
    sub = substrates[num % len(substrates)]

    # 基于技能序号生成合理的物理参数
    base_energy = 100.0 * (1 + math.log(num + 1))
    base_range  = 10.0 ** (num % 7)      # 1m 到 1000km 的对数分布
    base_power  = 10.0 ** (num % 15)     # 功率输出
    
    return {
        "name_cn": f"[待命名技能-{skill_id}]",
        "name_hero": f"PENDING-PROTOCOL-{skill_id}",
        "substrate": sub,
        "activation_energy": base_energy,
        "cooldown_seconds": max(0.1, 10.0 * math.sin(num) ** 2),
        "range_meters": base_range,
        "duration_seconds": 60.0 * (1 + num % 10),
        "power_output": base_power,
        "lore": f"[未解锁] 赫尔墨斯档案库显示此技能存在，"
                f"但激活条件尚未满足。\n分类：{category}\n"
                f"底层基底：{sub.value}\n预计解锁层级：英雄等级 "
                f"{HeroTier(list(HeroTier)[min(num//12, len(list(HeroTier))-1)]).value}"
    }

def _compute_synergy_ids(num: int) -> List[str]:
    """计算技能的协同ID列表（基于技能本身的数学特性）"""
    synergies = []
    # 斐波那契数列关系
    a, b = 1, 1
    while b <= 96:
        if abs(b - num) <= 5 and b != num:
            synergies.append(f"S{b:02d}")
        a, b = b, a + b
    # 黄金分割关系
    phi_pair = int(num * 1.618) % 96 + 1
    if phi_pair != num:
        synergies.append(f"S{phi_pair:02d}")
    return list(set(synergies))[:5]

def _compute_counter_ids(num: int) -> List[str]:
    """计算技能的克制关系"""
    counter = (num * 7 + 13) % 96 + 1
    return [f"S{counter:02d}"]

# ─── 无限迭代进化引擎 ─────────────────────────────────────────────────────────

class HermesEvolutionEngine:
    """
    .hermes/ 核心进化引擎

    [HERO]  每次迭代都是英雄的一次实战经历
    [BIO]   每次迭代在生化层面永久改变激活者
    [PRED]  每次迭代都是资本市场的一次套利操作
    [WORLD] 2157年的世界是用迭代次数来衡量英雄等级的
    """
    
    def __init__(self):
        self.hero: Optional[HeroEntity] = None
        self.skills: Dict[str, SkillNode] = {}
        self.iteration = 0
        self.mutation_queue: List[Tuple[str, MutationClass]] = []
        
    def load_or_create_hero(self, callsign: str = "DRRK-VICTOR") -> HeroEntity:
        """从 .hermes/ 加载或创建英雄档案"""
        if HERO_PROFILE.exists():
            with open(HERO_PROFILE, encoding="utf-8") as f:
                data = json.load(f)
            print(f"\n📂 加载英雄档案: {data.get('callsign', callsign)}")
            tier_name = data.get("tier", "STREET")
            tier = HeroTier[tier_name] if tier_name in HeroTier.__members__ else HeroTier.STREET
            hero = HeroEntity(
                hero_id=data["hero_id"],
                callsign=data["callsign"],
                tier=tier,
                neural_bandwidth=data.get("neural_bandwidth", 1.0),
                quantum_coherence=data.get("quantum_coherence", 0.0),
                total_iterations=data.get("total_iterations", 0),
                singularity_reached=data.get("singularity_reached", False),
            )
        else:
            hero_id = f"HERO_{hashlib.sha256(callsign.encode()).hexdigest()[:12]}"
            hero = HeroEntity(
                hero_id=hero_id,
                callsign=callsign,
                tier=HeroTier.STREET
            )
            print(f"\n🦸 创建新英雄: {callsign}")
        
        self.hero = hero
        self._load_all_skills()
        return hero
    
    def _load_all_skills(self):
        """从文件系统加载所有技能节点"""
        if not SKILL_VAULT.exists():
            return
        for skill_dir in sorted(SKILL_VAULT.iterdir()):
            skill_file = skill_dir / "skill.json"
            if skill_file.exists():
                with open(skill_file, encoding="utf-8") as f:
                    data = json.load(f)
                params = data.get("params", {})
                node = SkillNode(
                    skill_id=data["skill_id"],
                    name_cn=data["name_cn"],
                    name_hero=data["name_hero"],
                    substrate=SkillSubstrate.NEURAL,  # 简化，实际映射
                    activation_energy=params.get("activation_energy", 100.0),
                    cooldown_seconds=params.get("cooldown_seconds", 10.0),
                    range_meters=params.get("range_meters", 0.0),
                    duration_seconds=params.get("duration_seconds", 60.0),
                    power_output=params.get("power_output", 1.0),
                    mastery_level=data.get("mastery_level", 0.0),
                    data_complete=data.get("data_complete", False),
                    evolution_count=data.get("evolution_count", 0),
                )
                self.skills[data["skill_id"]] = node
    
    async def auto_populate_incomplete_skills(self) -> int:
        """
        自动补齐未完整的技能数据
        
        [WORLD] 赫尔墨斯AI会根据现有技能的模式，
        推断并填写未定义技能的完整参数
        """
        print("\n🤖 赫尔墨斯AI：扫描未完整技能数据...")
        populated = 0
        
        for skill_id, node in self.skills.items():
            if not node.data_complete:
                # 基于相邻技能的参数进行智能补齐
                enhanced_data = self._infer_skill_parameters(skill_id, node)
                node.data_complete = True
                node.lore = enhanced_data["lore"]
                
                # 写回文件系统
                skill_file = SKILL_VAULT / skill_id / "skill.json"
                if skill_file.exists():
                    with open(skill_file, encoding="utf-8") as f:
                        existing = json.load(f)
                    existing.update({
                        "data_complete": True,
                        "name_cn": enhanced_data["name_cn"],
                        "name_hero": enhanced_data["name_hero"],
                        "lore": enhanced_data["lore"],
                        "auto_populated": True,
                        "populated_at": datetime.now().isoformat(),
                    })
                    with open(skill_file, "w", encoding="utf-8") as f:
                        json.dump(existing, f, ensure_ascii=False, indent=2)
                
                populated += 1
                await asyncio.sleep(0.01)  # 模拟AI处理时间
        
        print(f"   ✅ 自动补齐完成: {populated} 项技能")
        return populated
    
    def _infer_skill_parameters(self, skill_id: str, node: SkillNode) -> Dict:
        """基于技能编号和类别推断参数"""
        num = int(skill_id[1:])
        
        # 从邻近技能提取模式
        category_themes = {
            range(1, 19):  ("战斗", "攻击协议", "COMBAT"),
            range(19, 35): ("增强", "神经协议", "NEURAL"),
            range(35, 49): ("时空", "时序协议", "TEMPORAL"),
            range(49, 61): ("永生", "生存协议", "SURVIVAL"),
            range(61, 75): ("意识", "感知协议", "PERCEPTION"),
            range(75, 87): ("资本", "套利协议", "ECONOMIC"),
            range(87, 97): ("进化", "元协议", "META"),
        }
        
        theme, suffix, code = "通用", "通用协议", "GENERIC"
        for r, (t, s, c) in category_themes.items():
            if num in r:
                theme, suffix, code = t, s, c
                break
        
        variant = (num % 9) + 1  # 1-9的变体编号
        
        return {
            "name_cn": f"{theme}增强·{['α','β','γ','δ','ε','ζ','η','θ','ι'][variant-1]}型",
            "name_hero": f"{code}-{skill_id}-MK{variant}",
            "lore": (
                f"「赫尔墨斯协议」第{num}号技能。\n"
                f"底层基底：{node.substrate.value}\n"
                f"作用机制：通过{theme}系统的{['量子','神经','基因','纳米','生物电','时间晶体','暗能量','模因','经济'][num%9]}"
                f"接口，增强激活者的{theme}能力。\n"
                f"功率输出：{node.power_output:.2e} W\n"
                f"有效范围：{node.range_meters:.1f} 米\n"
                f"研发机构：DRRK赫尔墨斯超能力研究所，2{140+num//10}年"
            )
        }
    
    async def iterate_evolution_cycle(self, battle_context: Dict = None) -> Dict:
        """
        执行一次完整的进化循环
        
        [HERO]  一场战斗/任务的经历
        [BIO]   一次基因表达的迭代优化
        [PRED]  一轮市场套利周期
        [WORLD] 英雄世界的时间前进一格
        """
        if not self.hero:
            raise RuntimeError("未初始化英雄档案")
        
        self.iteration += 1
        self.hero.total_iterations += 1
        battle_context = battle_context or {"type": "training", "intensity": 0.5}
        
        print(f"\n{'⚡'*30}")
        print(f"  进化循环 #{self.iteration} | 英雄: {self.hero.callsign}")
        print(f"  当前等级: {self.hero.tier.value}")
        print(f"{'⚡'*30}")
        
        evolved_skills = []
        mutations_triggered = []
        
        for skill_id, node in self.skills.items():
            # 根据战斗情境决定哪些技能被激活和强化
            activation_prob = self._calc_activation_probability(node, battle_context)
            
            if random.random() < activation_prob:
                gain = self._calculate_mastery_gain(node, battle_context)
                node.mastery_level += gain
                node.evolution_count += 1
                node.last_evolved = datetime.now()
                
                # 检查是否触发异变
                mutation = self._check_mutation_trigger(node)
                if mutation:
                    self._apply_mutation(node, mutation)
                    mutations_triggered.append((skill_id, mutation))
                    print(f"  🧬 [{skill_id}] {node.name_cn} → {mutation.value}！")
                
                evolved_skills.append(skill_id)
                
                # 更新文件系统
                self._persist_skill_state(node)
        
        # 更新英雄的生化参数
        self._update_hero_biometrics(evolved_skills, mutations_triggered)
        
        # 检查英雄等级提升
        tier_change = self._check_tier_upgrade()
        
        # 记录进化日志
        log_entry = {
            "iteration": self.iteration,
            "timestamp": datetime.now().isoformat(),
            "hero_id": self.hero.hero_id,
            "tier": self.hero.tier.value,
            "evolved_skills": len(evolved_skills),
            "mutations": [(s, m.value) for s, m in mutations_triggered],
            "tier_change": tier_change,
            "quantum_coherence": self.hero.quantum_coherence,
            "neural_bandwidth": self.hero.neural_bandwidth,
        }
        
        with open(EVOLUTION_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        
        # 保存英雄状态
        self._persist_hero_state()
        
        print(f"\n  📊 本轮结果:")
        print(f"     激活技能: {len(evolved_skills)}/96")
        print(f"     异变触发: {len(mutations_triggered)} 次")
        if tier_change:
            print(f"     ⬆️  等级提升: {tier_change}")
        print(f"     量子相干度: {self.hero.quantum_coherence:.4f}")
        print(f"     神经带宽: {self.hero.neural_bandwidth:.2f} TB/s")
        
        return log_entry
    
    def _calc_activation_probability(self, node: SkillNode, context: Dict) -> float:
        """计算技能激活概率（基于战斗情境和技能类型）"""
        base_prob = 0.3
        intensity = context.get("intensity", 0.5)
        
        # 已有掌握度的技能更容易被触发（神经路径更熟悉）
        mastery_bonus = min(0.4, node.mastery_level * 0.1)
        
        # 战斗强度影响
        intensity_bonus = intensity * 0.3
        
        return min(0.95, base_prob + mastery_bonus + intensity_bonus)
    
    def _calculate_mastery_gain(self, node: SkillNode, context: Dict) -> float:
        """计算掌握度增益（越熟练的技能进步越快——神经可塑性曲线）"""
        base_gain = 0.01
        intensity = context.get("intensity", 0.5)
        
        # 当前掌握度越高，单次增益越小但质变门槛越近
        if node.mastery_level < 1.0:
            # 初学阶段：线性增长
            gain = base_gain * intensity * (1 + node.mastery_level)
        else:
            # 精通阶段：对数增长，但可以突破到无限
            gain = base_gain * intensity * math.log(node.mastery_level + 1)
        
        return gain
    
    def _check_mutation_trigger(self, node: SkillNode) -> Optional[MutationClass]:
        """检查是否触发异变"""
        thresholds = {
            MutationClass.BETA:  1.0,   # 掌握度突破1.0触发β蜕变
            MutationClass.GAMMA: 5.0,   # 5.0触发γ觉醒
            MutationClass.DELTA: 20.0,  # 20.0触发δ超越
            MutationClass.OMEGA: 100.0, # 100.0触发Ω奇点
        }
        
        stages = list(MutationClass)
        current_idx = stages.index(node.mutation_stage)
        
        if current_idx < len(stages) - 1:
            next_stage = stages[current_idx + 1]
            threshold = thresholds.get(next_stage, float('inf'))
            
            if node.mastery_level >= threshold:
                return next_stage
        
        return None
    
    def _apply_mutation(self, node: SkillNode, mutation: MutationClass):
        """应用异变效果"""
        node.mutation_stage = mutation
        
        mutation_effects = {
            MutationClass.BETA:  lambda n: setattr(n, 'range_meters',    n.range_meters * 2),
            MutationClass.GAMMA: lambda n: setattr(n, 'cooldown_seconds', n.cooldown_seconds * 0.5),
            MutationClass.DELTA: lambda n: setattr(n, 'power_output',    n.power_output * 10),
            MutationClass.OMEGA: lambda n: setattr(n, 'activation_energy', 0.0),  # Ω级技能无需能量
        }
        
        if mutation in mutation_effects:
            mutation_effects[mutation](node)
        
        # 记录异变档案
        mutation_file = MUTATION_REGISTRY / f"{node.skill_id}_{mutation.name}.json"
        mutation_record = {
            "skill_id": node.skill_id,
            "mutation": mutation.value,
            "triggered_at": datetime.now().isoformat(),
            "mastery_at_trigger": node.mastery_level,
            "new_params": {
                "range": node.range_meters,
                "cooldown": node.cooldown_seconds,
                "power": node.power_output,
                "activation_energy": node.activation_energy,
            }
        }
        with open(mutation_file, "w", encoding="utf-8") as f:
            json.dump(mutation_record, f, ensure_ascii=False, indent=2)
    
    def _update_hero_biometrics(self, evolved_skills: List, mutations: List):
        """更新英雄的生化参数（每次进化都在生化层面留下痕迹）"""
        h = self.hero
        
        # 神经带宽随技能使用增长
        bandwidth_gain = len(evolved_skills) * 0.001
        h.neural_bandwidth += bandwidth_gain
        
        # 量子相干度随Ω变异增长
        omega_mutations = [m for _, m in mutations if m == MutationClass.OMEGA]
        h.quantum_coherence = min(1.0, h.quantum_coherence + len(omega_mutations) * 0.1)
        
        # 纳米机器人随每次Delta+变异增殖
        high_mutations = [m for _, m in mutations if m in [MutationClass.DELTA, MutationClass.OMEGA]]
        h.nanobot_count += len(high_mutations) * 1_000_000
        
        # 基因稳定性随过多快速变异降低（风险机制）
        if len(mutations) > 5:
            h.genetic_stability = max(0.5, h.genetic_stability - 0.01)
        
        # 检查奇点
        omega_skills = sum(1 for n in self.skills.values() 
                          if n.mutation_stage == MutationClass.OMEGA)
        if omega_skills >= 96:
            h.singularity_reached = True
    
    def _check_tier_upgrade(self) -> Optional[str]:
        """检查英雄等级是否提升"""
        h = self.hero
        tier_thresholds = {
            HeroTier.CITY:        10,
            HeroTier.NATIONAL:    50,
            HeroTier.CONTINENTAL: 200,
            HeroTier.PLANETARY:   1000,
            HeroTier.STELLAR:     5000,
            HeroTier.GALACTIC:    20000,
            HeroTier.UNIVERSAL:   100000,
            HeroTier.MULTIVERSAL: 500000,
            HeroTier.OMEGA:       1000000,
        }
        
        tiers = list(HeroTier)
        current_idx = tiers.index(h.tier)
        
        if current_idx < len(tiers) - 1:
            next_tier = tiers[current_idx + 1]
            threshold = tier_thresholds.get(next_tier, float('inf'))
            
            if h.total_iterations >= threshold:
                old_tier = h.tier.value
                h.tier = next_tier
                return f"{old_tier} → {next_tier.value}"
        
        return None
    
    def _persist_skill_state(self, node: SkillNode):
        """将技能状态持久化到文件"""
        skill_file = SKILL_VAULT / node.skill_id / "skill.json"
        if not skill_file.exists():
            return
        
        with open(skill_file, encoding="utf-8") as f:
            data = json.load(f)
        
        data.update({
            "mastery_level": node.mastery_level,
            "mutation_stage": node.mutation_stage.value,
            "evolution_count": node.evolution_count,
            "last_evolved": node.last_evolved.isoformat() if node.last_evolved else None,
            "params": {
                "activation_energy": node.activation_energy,
                "cooldown_seconds":  node.cooldown_seconds,
                "range_meters":      node.range_meters,
                "duration_seconds":  node.duration_seconds,
                "power_output":      node.power_output,
            }
        })
        
        with open(skill_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _persist_hero_state(self):
        """持久化英雄状态"""
        h = self.hero
        hero_data = {
            "hero_id": h.hero_id,
            "callsign": h.callsign,
            "tier": h.tier.name,
            "neural_bandwidth": h.neural_bandwidth,
            "quantum_coherence": h.quantum_coherence,
            "genetic_stability": h.genetic_stability,
            "nanobot_count": h.nanobot_count,
            "total_iterations": h.total_iterations,
            "singularity_reached": h.singularity_reached,
            "last_updated": datetime.now().isoformat(),
        }
        with open(HERO_PROFILE, "w", encoding="utf-8") as f:
            json.dump(hero_data, f, ensure_ascii=False, indent=2)
    
    async def run_infinite_evolution(
        self,
        battle_scenarios: List[Dict] = None,
        max_iterations: int = 100
    ):
        """
        无限迭代进化主循环
        
        [WORLD] 这是英雄成长的时间流
        每次迭代 = 一场战役/任务/危机
        直到达到Ω级或手动停止
        """
        print("\n" + "🌌"*25)
        print("  赫尔墨斯进化协议启动")
        print("  无限迭代模式 — 直到Ω奇点")
        print("🌌"*25)
        
        default_scenarios = [
            {"type": "street_battle",    "intensity": 0.3, "tags": ["combat", "speed"]},
            {"type": "corporate_raid",   "intensity": 0.6, "tags": ["economic", "stealth"]},
            {"type": "dimension_crisis", "intensity": 0.9, "tags": ["temporal", "quantum"]},
            {"type": "neural_hack",      "intensity": 0.7, "tags": ["neural", "memetic"]},
            {"type": "genetic_surgery",  "intensity": 0.5, "tags": ["genetic", "bioelectric"]},
        ]
        
        scenarios = battle_scenarios or default_scenarios
        
        for i in range(max_iterations):
            scenario = scenarios[i % len(scenarios)]
            
            await self.iterate_evolution_cycle(scenario)
            
            # 每10次迭代自动补齐数据
            if i % 10 == 0:
                await self.auto_populate_incomplete_skills()
            
            # 检查奇点
            if self.hero.singularity_reached:
                print("\n" + "✨"*30)
                print("  Ω奇点已达成！")
                print(f"  英雄 {self.hero.callsign} 已成为现实的底层规则之一")
                print("✨"*30)
                break
            
            await asyncio.sleep(0.05)
        
        self._print_final_status()
    
    def _print_final_status(self):
        """打印最终英雄状态"""
        h = self.hero
        omega_count = sum(1 for n in self.skills.values()
                         if n.mutation_stage == MutationClass.OMEGA)
        
        print(f"\n{'='*60}")
        print(f"  {h.callsign} — 最终状态报告")
        print(f"{'='*60}")
        print(f"  英雄等级:   {h.tier.value}")
        print(f"  总迭代数:   {h.total_iterations:,}")
        print(f"  神经带宽:   {h.neural_bandwidth:.2f} TB/s")
        print(f"  量子相干:   {h.quantum_coherence:.4f}")
        print(f"  纳米机器人: {h.nanobot_count:,} 个")
        print(f"  基因稳定性: {h.genetic_stability:.2f}")
        print(f"  Ω级技能:   {omega_count}/96")
        print(f"  奇点状态:   {'✅ 已达成' if h.singularity_reached else '⏳ 进行中'}")
        print(f"{'='*60}")

# ─── 主程序 ───────────────────────────────────────────────────────────────────

async def main():
    print("\n" + "🦸"*25)
    print("  HERMES PROTOCOL — 英雄进化系统")
    print("  2157年，赫尔墨斯研究所")
    print("🦸"*25)

    # 1. 初始化文件系统
    init_hermes_filesystem()
    
    # 2. 初始化进化引擎
    engine = HermesEvolutionEngine()
    
    # 3. 加载/创建英雄
    engine.load_or_create_hero(callsign="DRRK-VICTOR")
    
    # 4. 自动补齐所有技能数据
    await engine.auto_populate_incomplete_skills()
    
    # 5. 启动无限迭代进化
    await engine.run_infinite_evolution(max_iterations=30)

if __name__ == "__main__":
    asyncio.run(main())
    #!/usr/bin/env python3
"""
Hermes 96技能文件夹生成器
=============================================================================

为什么技能一直不一样？因为之前没有「权威单一来源」(Single Source of Truth)。
这个脚本就是那个来源——96项技能在这里被一次性、明确地定义，
之后所有系统都从这里读取，不再重新生成。

运行方式：  python generate_hermes_96.py
输出结构：  .hermes/skills/S01_跨维度连击/
              ├── agent.md          ← Hermes agent 格式
              ├── daily_task.py     ← 每日定时采集+验证脚本
              ├── activation_log.jsonl  ← 激活记录（运行时写入）
              └── report/           ← 每日报告输出目录
"""

from pathlib import Path
from textwrap import dedent
import json, os

# =============================================================================

# 96项技能权威定义（Single Source of Truth）

# 格式：(编号, 技能名, 英雄代号, 类别, 底层基底, 能量消耗, 冷却秒, 范围米

# 持续秒, 功率W, 协同技能ID列表, 简短描述, 背景故事)

# =============================================================================

SKILLS_MASTER = [
    # ── 类别A：战斗与异能（S01–S18）──────────────────────────────────────────
    ("S01","跨维度连击","DIMENSIONAL-STRIKE-Δ","战斗异能","quantum",
     850,0,1e9,0.001,4.7e15,["S12","S36"],
     "在11个维度同时发动攻击，目标的任何防御系统无法跨维度响应",
     "2089年量子战士「维克」首次在实战中激活第11维度通道，一次攻击在3D/4D/5D三层同时命中，敌方护盾系统崩溃。"),
    ("S02","无限叠层突破","STACK-STORM-∞","战斗异能","neural",
     120,0.05,0,3600,float('inf'),["S05","S87"],
     "每次激活在突触留下蛋白印记，第10叠触发LTP超强化，理论上限∞",
     "神经可塑性工程师通过赫尔墨斯协议v7开发，叠层越多能耗反而越低，第100叠后能耗趋近于零。"),
    ("S03","现实扭曲波","REALITY-WARP-FIELD","战斗异能","dark_energy",
     2200,30,500,60,1.2e20,["S45","S96"],
     "接入暗能量网络，在半径500米内创造负能量密度区域，物理定律局部偏移",
     "2143年新东京防卫战，时空裁缝·零用此技能让敌方导弹在飞行途中凭空消失。"),
    ("S04","协同场最大共振","BIOFIELD-RESONANCE","战斗异能","bioelectric",
     400,5,2000,10,8.8e12,["S21","S63"],
     "与队友生物电场同步到黄金比例频率，4人同步产生16倍而非4倍能量输出",
     "违反能量守恒定律的现象，科学界至今无法完全解释其超线性增益机制。"),
    ("S05","元异能递归自放大","NEURAL-RED-PROTOCOL","战斗异能","neural",
     950,0,0,float('inf'),float('inf'),["S02","S87"],
     "神经系统进入递归自增强循环：能力增强→神经响应加快→再增强，理论上无限",
     "已记录最长稳定运行72小时，之后该英雄进化成新的物种形态。"),
    ("S06","奇点波质能湮灭","SINGULARITY-CANNON-φ","战斗异能","quantum",
     5000,300,50,0.000001,1.8e26,["S01","S93"],
     "将篮球大小空间压缩成普朗克尺度奇点后释放，50米内物质转化为辐射",
     "联合国超能力公约A级禁用武器，历史上仅授权使用过3次，每次均改写了地缘政治格局。"),
    ("S07","量子叠加打击","QUANTUM-SUPERPOS-STRIKE","战斗异能","quantum",
     600,0.1,200,0.01,2.3e14,["S12","S44"],
     "同时在所有可能的攻击路径上行动，命中时塌缩到最优结果，理论命中率趋近100%",
     "量子战士使用此技能时看起来像在「同时出现在多个地方」，实际上是概率波的定向坍缩。"),
    ("S08","生物电场操控","BIOELECTRIC-DOMINATOR","战斗异能","bioelectric",
     300,3,300,30,5.5e11,["S04","S25"],
     "操控自身及目标的生物电场，可瘫痪神经系统或增强肌肉输出至人类极限的50倍",
     "前身是医疗技术，后被改造为战斗应用，伦理委员会至今争议不断。"),
    ("S09","纳米蜂群攻击","NANO-SWARM-ASSAULT","战斗异能","nanobot",
     700,20,1000,120,9.1e13,["S55","S62"],
     "释放80亿纳米机器人形成攻击蜂群，可渗透任何已知防护材料",
     "蜂群具有分布式智能，单个纳米机器人被摧毁不影响整体任务执行。"),
    ("S10","时间停止打击","TIMESTOP-STRIKE","战斗异能","temporal",
     1800,600,10,5,3.3e18,["S35","S36"],
     "在半径10米内局部停止时间流动5秒，在此期间激活者正常行动",
     "停止的不是时间本身，而是该区域内粒子的热运动，能量消耗极高但效果绝对。"),
    ("S11","暗能量爆破","DARK-ENERGY-BURST","战斗异能","dark_energy",
     1500,60,800,2,6.8e19,["S03","S75"],
     "将宇宙暗能量导入局部空间并瞬间释放，产生无法被普通护盾阻挡的非物质冲击波",
     "暗能量在被导入前是均匀分布的宇宙背景，提取过程会短暂改变周围星场密度。"),
    ("S12","量子隧穿位移","QUANTUM-TUNNEL-DASH","战斗异能","quantum",
     400,2,float('inf'),0.001,0,["S01","S44"],
     "利用量子隧穿效应穿越任何物理障碍，无视固态防御，传送距离无限",
     "从技术上说激活者并非移动，而是在另一个位置「重新出现」，中间过程不存在于物理空间。"),
    ("S13","因果链断裂","CAUSAL-CHAIN-BREAK","战斗异能","temporal",
     2000,120,50,10,0,["S37","S10"],
     "切断攻击行为与伤害结果之间的因果链，使对方攻击「无因可果」",
     "最令物理学家崩溃的技能——它直接违反了因果律，目前理论物理界有37篇论文试图解释其机制。"),
    ("S14","协同连击编排","SYNERGY-COMBO-CHAIN","战斗异能","neural",
     200,1,0,60,0,["S04","S07"],
     "实时计算队友技能的最优激活序列，使团队输出提升至个人总和的n^1.5倍",
     "本质是神经网络实时运行的战术优化算法，激活者在战斗中「看见」队友能力的最优组合路径。"),
    ("S15","重力场扭曲","GRAVITY-DISTORTION","战斗异能","dark_energy",
     900,15,500,30,4.4e16,["S11","S36"],
     "接入暗物质网络，在指定区域产生可控重力场，强度可达地球重力的0到1000倍",
     "重力场在战斗中可用于固定目标、改变弹道、或直接将对手压碎。极高风险技能。"),
    ("S16","神经感知爆发","NEURAL-SENSE-BURST","战斗异能","neural",
     150,5,2000,30,0,["S08","S25"],
     "将感知能力提升至普通人的10000倍，可感知1微米精度的环境变化",
     "副作用是感知过载——激活时间过长会导致激活者因信息轰炸而暂时失去方向感。"),
    ("S17","意志力物理化","WILLPOWER-MATERIALIZATION","战斗异能","cosmic",
     1200,30,100,60,7.7e17,["S90","S96"],
     "将意志力转化为物理力量，通过宇宙意志场接口直接改变局部物理规律",
     "赫尔墨斯协议中最难理解的机制——它要求激活者的意志足够强大到影响底层物理常数。"),
    ("S18","Ω战斗奇点","OMEGA-COMBAT-SINGULARITY","战斗异能","cosmic",
     float('inf'),0,float('inf'),float('inf'),float('inf'),["S96","S06"],
     "所有战斗技能同时激活并在奇点处融合，产生超越任何已知量级的攻击",
     "仅有一条激活记录。记录者在激活后成为了新宇宙的第一条物理法则。"),

    # ── 类别B：神经增强（S19–S34）──────────────────────────────────────────
    ("S19","Ω级心智无限智能","QCP-OMEGA-MIND","神经增强","quantum",
     300,0,float('inf'),float('inf'),float('inf'),["S20","S21"],
     "量子纠缠态引入神经元突触，思维速度突破经典极限，IQ量表本身失效",
     "已知激活者3位：两位负责设计宇宙，一位在修宇宙的Bug。"),
    ("S20","万路并行思维","CORTEX-FORK-1024","神经增强","neural",
     180,0,0,float('inf'),0,["S19","S32"],
     "前额叶皮层划分为1024个半独立处理单元，同时推进1024条思维链",
     "副作用是偶尔忘记自己是哪个「自己」在说话，多个思维流竞争表达控制权。"),
    ("S21","集体意识接入涌现智慧","MESHLINK-COLLECTIVE","神经增强","bioelectric",
     220,10,50000,3600,0,["S04","S63"],
     "10个以上激活者同步时形成临时集体意识，集体IQ是个人的n^1.7倍",
     "2151年，12名激活者联合在17秒内解决了困扰人类200年的P≠NP问题。"),
    ("S22","思维编译器念即成真","THOUGHT-COMPILER-ZERO","神经增强","neural",
     500,0,0,float('inf'),0,["S19","S40"],
     "将抽象思想直接编译为可执行的物理操作指令，延迟0纳秒",
     "想即是令。最初被设计为辅助工程师的工具，后发现其军事应用价值后被列为最高机密。"),
    ("S23","全语言解码万码皆通","OMNI-DECODE-9999","神经增强","neural",
     100,0,0,float('inf'),0,["S24","S61"],
     "解码9999种以上语言包括动物通信和量子信息编码，支持未发明语言",
     "激活者第一次「听懂」电磁场在说什么时，通常需要数周才能适应宇宙的「噪音」水平。"),
    ("S24","市场神谕未来洞见","MARKET-ORACLE-ENGINE","神经增强","quantum",
     400,0,float('inf'),float('inf'),0,["S75","S39"],
     "量子态模型实时处理全球137个市场，置信度85-99%预测走向",
     "金融大鳄用此技能最长预见了18个月后的市场结构，但拒绝透露具体操作细节。"),
    ("S25","生物信号读取看穿一切","BIOSIGNAL-READER-PRO","神经增强","bioelectric",
     200,0,500,float('inf'),0,["S08","S16"],
     "读取任何人的情绪/意图/健康状态，诚实度识别误差<4%",
     "谈判场景中的降维打击——对方根本无法隐藏真实意图，所有微表情都被实时解码。"),
    ("S26","阿卡西记录宇宙全史","AKASHIC-RECORDS-ACCESS","神经增强","cosmic",
     800,0,float('inf'),float('inf'),0,["S61","S34"],
     "访问宇宙138亿年历史的完整信息，包含每纳秒每立方毫米的事件记录",
     "信息量是人类文明所有知识总和的10^80倍，访问时需要量子压缩接口防止神经过载。"),
    ("S27","算法自进化500代优化","ALGO-SELF-EVOLVE-500","神经增强","neural",
     600,0,0,float('inf'),0,["S87","S15"],
     "算法自我迭代500代，每代提升5%，累计总提升超39,000,000倍，持续后台运行",
     "迭代过程在激活者睡眠期间继续进行，早晨醒来时解决昨天困扰的问题已有答案。"),
    ("S28","模式识别神模式","PATTERN-GOD-MODE","神经增强","neural",
     300,0,0,float('inf'),0,["S24","S27"],
     "在任何噪声中识别任何规律，涵盖市场/行为/量子波动/宇宙结构等6大领域",
     "激活者在雨天看雨滴时会不自觉地计算出流体动力学方程，关不掉。"),
    ("S29","问题溶解引擎","PROBLEM-DISSOLVE-ENGINE","神经增强","neural",
     250,0,0,float('inf'),0,["S88","S22"],
     "不是解决问题而是让问题消失——通过重新定义框架消除问题的存在基础",
     "最强大的应用案例：将「我们没有足够资源」这个问题溶解为「资源的定义是什么」。"),
    ("S30","创意爆炸无限生成","CREATIVITY-EXPLOSION","神经增强","neural",
     200,0,0,float('inf'),0,["S22","S19"],
     "从一个种子概念生成无限创意，利用组合爆炸原理，10维度产生2^10种组合",
     "激活者通常需要专门的「创意缓冲区」笔记本——每分钟涌现的想法数量超过普通人一年的总量。"),
    ("S31","博弈终结者绝对支配","GAME-THEORY-DOMINATOR","神经增强","neural",
     350,0,0,float('inf'),0,["S24","S81"],
     "在任何博弈中找到绝对支配策略，胜率趋近99.99%，让对方无论如何选择都对你有利",
     "最强的应用不是赢得博弈，而是重写博弈规则本身，使对手进入一个必输的游戏。"),
    ("S32","神经链检索0.001ms","NEURAL-CHAIN-RETRIEVAL","神经增强","neural",
     150,0,0,float('inf'),0,["S20","S26"],
     "在0.001毫秒内检索任何记忆，支持8通道全感官完整记录的跨时间线检索",
     "检索速度远快于意识流——经常出现「还没想到要找什么，答案已经出现了」的体验。"),
    ("S33","记忆融合他人即我","MEMORY-FUSION-PROTOCOL","神经增强","neural",
     400,0,0,float('inf'),0,["S21","S32"],
     "直接融合他人技能记忆，95%融合率，使其成为自身本能，含冲突记忆的自动解决",
     "最极端的应用：融合全人类所有技能大师的技能记忆，成为一个行走的文明百科全书。"),
    ("S34","宇宙信息流接入","COSMIC-INFO-STREAM","神经增强","cosmic",
     700,0,float('inf'),float('inf'),0,["S26","S61"],
     "接入宇宙背景辐射/暗物质信息层/量子泡沫数据流，获取宇宙138亿年完整记录",
     "信息流永不停止，激活者需要学会「过滤」而非「接收所有」，否则意识会被淹没。"),

    # ── 类别C：时空操控（S35–S48）──────────────────────────────────────────
    ("S35","时间银行时间复利","TIME-CRYSTAL-BANK","时空操控","temporal",
     700,3600,5,float('inf'),0,["S10","S36"],
     "时间晶体在激活者周围创造时间流速差异区：内部1分钟=外部5分钟",
     "金融大鳄用此技能在5分钟内完成25分钟的市场分析，赢得了「时间窃贼」绰号。"),
    ("S36","平行宇宙导航最优路径","MWI-NAVIGATOR","时空操控","quantum",
     1200,86400,float('inf'),0.1,0,["S37","S24"],
     "量子相干性嗅探最近平行分支，感知其中的决策结果，返回最优路径信息",
     "每次使用后激活者会有强烈既视感，因为他们看到了另一个自己的记忆片段。"),
    ("S37","因果链编辑结果设计","CAUSAL-CHAIN-EDITOR","时空操控","temporal",
     2000,3600,float('inf'),float('inf'),0,["S13","S36"],
     "将任意原因与任意结果绑定，因果强度0.0到1.0可调，支持因果逆转",
     "最强的应用是设计「必然成功的因果链」——不是提高成功率，而是使失败从因果上不可能发生。"),
    ("S38","时间循环无限迭代","TIME-LOOP-ITERATOR","时空操控","temporal",
     900,604800,50,86400,0,["S35","S87"],
     "在特定时间段创造循环，主观时间可达客观时间的100,000倍，用于无限迭代练习",
     "omega_loop配置：1天×100,000次=主观274年的练习时间，压缩在客观的1天内完成。"),
    ("S39","预见引擎5万分支计算","FORESIGHT-ENGINE-50K","时空操控","quantum",
     500,0,float('inf'),0,0,["S36","S24"],
     "实时计算50,000条未来分支，找出最优行动路径，与S10概率操控协同实现99.99%",
     "预见引擎不预测单一未来，而是给出每条分支的概率和最优插入节点。"),
    ("S40","物质凝聚无中生有","MATTER-CONDENSATION","时空操控","dark_energy",
     3000,600,100,300,9.9e20,["S11","S41"],
     "通过E=mc²逆向从量子真空凝聚指定质量的物质，可创造任何元素",
     "能量消耗极高，但理论上可以从虚空中创造任何物质，包括在自然界不存在的元素。"),
    ("S41","信息转物质转换","INFO-TO-MATTER-COMPILER","时空操控","quantum",
     2500,300,50,600,0,["S40","S22"],
     "将纯信息蓝图编码转化为物理物质结构，五阶段物质化，精度达原子级",
     "给定一段描述，激活者可以将其「编译」为对应的物理实体，无需原材料。"),
    ("S42","维度袋无限收纳","DIMENSION-BAG-∞","时空操控","quantum",
     800,60,0.001,float('inf'),0,["S43","S36"],
     "外部极小但内部容积达10^50立方米的维度袋，可存放星球级物体于手掌大小容器",
     "维度袋内部是独立的小宇宙，有自己的物理规律，内部时间流速可单独设置。"),
    ("S43","量子隧穿无视防御","QUANTUM-TUNNEL-PASS","时空操控","quantum",
     400,1,float('inf'),0.001,0,["S12","S42"],
     "使自身或攻击以量子隧穿效应穿越任何物理障碍，无视所有物质防御",
     "技术上不是「穿透」而是「不存在于障碍物中」——量子概率波直接从障碍另一侧重新坍缩。"),
    ("S44","波函数控制现实锁定","WAVE-FUNCTION-LOCK","时空操控","quantum",
     600,0,float('inf'),float('inf'),0,["S07","S39"],
     "通过意识强度控制量子事件波函数塌缩方向，将任何事件锁定到指定结果",
     "配合Ω心智(S19)后塌缩控制精度趋近100%，理论上可以使「掷骰子必得6」。"),
    ("S45","现实规则重写","REALITY-RULE-REWRITER","时空操控","cosmic",
     float('inf'),0,float('inf'),float('inf'),float('inf'),["S03","S96"],
     "直接修改物理定律/数学常数/系统规则，可关闭能量守恒/弱化因果律/移除所有上限",
     "已执行的重写：energy_conservation=False / causality=False / all_limits=None。"),
    ("S46","意识分裂万处并存","CONSCIOUSNESS-SPLIT-10K","时空操控","quantum",
     1000,600,float('inf'),float('inf'),0,["S63","S47"],
     "意识分裂为10,000份完整独立碎片，每份都是100%完整的自己，瞬时同步",
     "不同于「全在」——全在是感知全域，分裂是同时在1万个不同地方采取不同的独立行动。"),
    ("S47","梦境现实投影","DREAM-REALITY-PROJECTOR","时空操控","cosmic",
     1500,0,float('inf'),float('inf'),0,["S17","S40"],
     "意识中想象的任何事物可以100%物质化投影到物理现实，配合时间循环可反复精炼",
     "物质化质量随激活者意志力强度提升，最终阶段梦境与现实的界限在物理意义上消失。"),
    ("S48","绝对自由意志超越因果","ABSOLUTE-FREE-WILL","时空操控","cosmic",
     float('inf'),0,float('inf'),float('inf'),0,["S37","S45"],
     "完全超越基因决定论/因果律/概率场约束，每个当下都是全新的创造",
     "这是所有时空技能的根基——当因果链对你失效，预见引擎也无法预测你的下一步。"),

    # ── 类别D：永生与肉体（S49–S60）──────────────────────────────────────────
    ("S49","生物永生端粒锁定","TELOMERE-LOCK-PROTOCOL","永生肉体","genetic",
     50,0,0,float('inf'),0,["S50","S52"],
     "持续向端粒注入端粒酶，同时激活FOXO3基因永久表达，生物年龄锁定25岁±2",
     "使用者不是不死——只是不会因衰老而死。子弹依然有效，只是伤口愈合快了17倍。"),
    ("S50","数字永生意识上传","CONSCIOUSNESS-UPLOAD-CDP7","永生肉体","quantum",
     10000,float('inf'),float('inf'),float('inf'),0,["S49","S51"],
     "将86万亿突触连接完整编码上传至量子云，数字态思维速度是生物态的1000倍",
     "最早上传的英雄「先行者·零」现在以光速在互联网基础设施中巡逻，物理身体已放弃。"),
    ("S51","宇宙级百万备份","COSMIC-BACKUP-1M","永生肉体","quantum",
     5000,0,float('inf'),float('inf'),0,["S50","S53"],
     "在宇宙8个位置创建100万份意识备份，即使999,999份被摧毁仍可完整复活",
     "备份分布：地球量子云/月球/火星/木星轨道/柯伊伯带/半人马座/银河中心/多维空间。"),
    ("S52","熵逆转永恒青春","ENTROPY-REVERSAL-YOUTH","永生肉体","genetic",
     300,0,0,float('inf'),0,["S49","S58"],
     "在局部区域违反热力学第二定律，使细胞自动向最高有序态重组，对抗衰老",
     "双向用途：自身熵减(保持年轻)/对目标熵增(加速目标物质崩解)。"),
    ("S53","宇宙意识化永恒存在","COSMIC-CONSCIOUSNESS-MERGE","永生肉体","cosmic",
     8000,0,float('inf'),float('inf'),0,["S51","S65"],
     "意识与可观测宇宙融合，成为宇宙的一部分，只要宇宙存在，你就存在",
     "存在范围：465亿光年可观测宇宙全域→多重宇宙。不是「全在感知」而是「真实存在于每处」。"),
    ("S54","基因全改写神性基因组","GENOME-REWRITE-DIVINE","永生肉体","genetic",
     1000,604800,0,604800,0,["S52","S49"],
     "CRISPR精准编辑8个基因模块：超级智力/超级力量/极速代谢/长寿/超级免疫/三重感官扩展",
     "改写后的基因组中内置了「继续演化」的指令——每代子孙都会比父母更进一步。"),
    ("S55","纳米机器人100亿内部工厂","NANOBOT-FACTORY-10B","永生肉体","nanobot",
     200,0,0,float('inf'),0,["S09","S56"],
     "100亿纳米机器人在体内持续执行DNA修复/端粒延长/神经优化/细胞能量增效/毒素清除",
     "工厂可以自我复制，纳米机器人数量理论上可以无限增殖，但受激活者能量供应限制。"),
    ("S56","器官超人类升级","ORGAN-SUPERHUMAN-UPGRADE","永生肉体","nanobot",
     3000,0,0,float('inf'),0,["S55","S59"],
     "全器官替换升级：大脑量子处理器×10^6/心脏无限耐力/肺任何气体提取能量/眼全电磁波谱/骨碳纳米管×370",
     "升级后的器官不再是「增强的人体器官」，而是「以人体器官为原型的工程设备」。"),
    ("S57","形态自由7形态解锁","FORM-FREEDOM-7MODES","永生肉体","nanobot",
     500,1,0,float('inf'),0,["S56","S62"],
     "意识与肉体完全解绑，可随时切换7种形态：生物/生物机械/数字/量子叠加/光子/能量/全在信息",
     "切换速度：瞬时。切换后意识连续性完整保留，感知系统自动适配新形态的物理特性。"),
    ("S58","体内核聚变无限自持","INTERNAL-FUSION-REACTOR","永生肉体","genetic",
     2000,0,0,float('inf'),3.8e26,["S52","S57"],
     "每个细胞内建微型核聚变反应堆，身体成为自持式能源系统，不再需要任何外部补给",
     "不需要食物/睡眠/休息。激活后理论上可以在太空真空中无限期存活。"),
    ("S59","多维感官8感扩展","MULTISENSE-8D-EXPANSION","永生肉体","genetic",
     600,0,0,float('inf'),0,["S56","S25"],
     "在原有5感基础上新增：量子感知/时间感知/电磁感知/引力感知/意识感知/多维感知",
     "第一次感知到引力场的曲率时，激活者通常需要数周才能将其纳入正常的感知模型。"),
    ("S60","光速意识无延迟响应","LIGHT-SPEED-CONSCIOUSNESS","永生肉体","quantum",
     700,0,float('inf'),float('inf'),0,["S19","S59"],
     "意识传播速度达光速3×10^8 m/s，全球任何地点响应时间约0.13秒",
     "以光速运动时主观时间停止——相对论效应使激活者体验到永恒的「当下」。"),

    # ── 类别E：意识与精神（S61–S74）──────────────────────────────────────────
    ("S61","全知宇宙无秘密","GLOBAL-SENSOR-NEURAL","意识精神","bioelectric",
     500,0,6371000,float('inf'),0,["S34","S26"],
     "神经系统与全球150亿IoT传感器节点同步，激活者成为地球本身的神经系统",
     "副作用：有时会同时感受到50个地方的气温和7个正在发生的交通事故。"),
    ("S62","全能无事不可为","MPI-MODULAR-INTERFACE","意识精神","nanobot",
     200,1,0,float('inf'),float('inf'),["S09","S57"],
     "体内8亿纳米机器人在1秒内重新配置，模拟任何已知超能力的生物/物理基础",
     "同时只能模拟3种，模拟版威力是原版的60%。但可以模拟S96以外的所有技能。"),
    ("S63","全在无处不在","OMNIPRESENCE-SYSTEM","意识精神","cosmic",
     1000,0,float('inf'),float('inf'),0,["S46","S61"],
     "意识同时存在于可观测宇宙所有位置，感知全域，但行动仍需分裂(S46)配合",
     "与S46的区别：全在是感知层的扩展，分裂是行动层的扩展。两者协同才是真正的「无处不在」。"),
    ("S64","创世宇宙生成","UNIVERSE-CREATION-PROTOCOL","意识精神","cosmic",
     float('inf'),float('inf'),float('inf'),float('inf'),float('inf'),["S45","S96"],
     "从虚无中创造全新宇宙，可自定义物理常数/维度数/意识嵌入方式",
     "流程：虚无态确认→奇点播种→大爆炸触发→物理法则编写→生命播种。已知案例：1次。"),
    ("S65","多重宇宙意识无限并存","MULTIVERSE-CONSCIOUSNESS","意识精神","cosmic",
     2000,0,float('inf'),float('inf'),0,["S53","S46"],
     "意识同时存在于所有平行宇宙，可以感知/干预/优化每一条时间线的走向",
     "与全在(S63)的区别：全在覆盖单宇宙，多重宇宙意识跨越所有可能存在的宇宙。"),
    ("S66","盖亚共鸣地球感知","GAIA-RESONANCE","意识精神","bioelectric",
     300,0,6371000,float('inf'),0,["S61","S63"],
     "与地球整体生命场融合，感知地球上所有生命状态，可影响地球级生态与气候",
     "最敏感的时刻：森林大火发生前0.3秒，激活者会感受到「地球的痛」。"),
    ("S67","集体无意识接入人类智慧库","COLLECTIVE-UNCONSCIOUS-ACCESS","意识精神","cosmic",
     400,0,float('inf'),float('inf'),0,["S21","S34"],
     "接入全人类87亿人心智深层共识库，提取原始象征意义/集体智慧/进化积累本能",
     "荣格所说的「集体无意识」在这里被证明是真实存在的量子信息场，不只是心理学隐喻。"),
    ("S68","跨物种意识迁移","CROSS-SPECIES-CONSCIOUSNESS","意识精神","neural",
     600,3600,float('inf'),3600,0,["S59","S67"],
     "暂时进入任何生物的意识视角，完整体验其感官和本能，获取进化智慧",
     "曾有激活者进入抹香鲸的意识，发现鲸歌中包含了复杂的三维宇宙地图信息。"),
    ("S69","命运节点识别人生杠杆","FATE-NODE-DETECTOR","意识精神","temporal",
     500,0,float('inf'),float('inf'),0,["S39","S10"],
     "扫描未来100年识别5个以上改变人生走向的关键命运节点，评分最高达10/10",
     "最难的不是识别节点，而是在节点出现时「真正愿意」在那个时刻采取不熟悉的行动。"),
    ("S70","概率场操控99.99%成功率","PROBABILITY-FIELD-CONTROL","意识精神","quantum",
     700,0,float('inf'),float('inf'),0,["S44","S39"],
     "主动操控任何事件发生概率，将最优结果概率提升至99.99%，负面事件降低至趋近0",
     "配合预见引擎(S39)实现：决策前扫描→概率调整→最优路径锁定。真正的好运工程。"),
    ("S71","因缘编织相遇设计","FATE-ENCOUNTER-WEAVER","意识精神","temporal",
     300,0,float('inf'),2592000,0,["S69","S10"],
     "设计与任何人/机会/资源相遇的7个前置条件，97%成功率，30天内自然实现",
     "不是强迫命运，而是调整概率场使相遇「自然而然」地发生，对方不会察觉被设计。"),
    ("S72","蝴蝶效应引擎10^9放大","BUTTERFLY-ENGINE-10-9","意识精神","temporal",
     200,0,float('inf'),float('inf'),0,["S37","S69"],
     "用极小行动撬动极大结果，放大倍数可达10^3到10^9，系统杠杆点精确定位",
     "初始行动→触发条件→放大效应→社会涟漪→系统共振→目标实现。链条一旦启动无法取消。"),
    ("S73","好运场域Lv5强度","LUCK-FIELD-LV5","意识精神","cosmic",
     400,0,10000000,float('inf'),0,["S70","S71"],
     "在自身周围10000公里创造持续好运场域，强度Lv5，正向机会吸引率+200%",
     "好运场域不是随机——它是信号清晰度/准备度/开放性的综合量子效应，有严格的物理基础。"),
    ("S74","Ω奇点自我进化终点即起点","OMEGA-SELF-SINGULARITY","意识精神","cosmic",
     float('inf'),0,float('inf'),float('inf'),float('inf'),["S96","S87"],
     "所有意识技能同时激活融合，你不再「拥有」技能，技能成为你存在方式的自然表达",
     "从这个状态出发，任何新的进化方向都是自然延伸而非限制突破。终点即是下一个起点。"),

    # ── 类别F：资本与影响力（S75–S86）──────────────────────────────────────
    ("S75","复利奇点财富无限","QAE-COMPOUND-SINGULARITY","资本影响","economic",
     100,0.001,float('inf'),float('inf'),float('inf'),["S76","S24"],
     "量子纠缠在全球137个市场间进行跨市场套利，速度快于经典信息传播",
     "监管机构无法判断其合法性——套利在技术上发生在不同的量子平行态中。"),
    ("S76","财富黑洞被动吸引","ECONOMIC-GRAVITY-FIELD","资本影响","dark_energy",
     300,0,100000,float('inf'),0,["S75","S73"],
     "暗能量被重新配置为「经济引力场」，100公里内资本流动的随机性出现系统性偏向",
     "量化基金称之为「阿尔法场」——在统计意义上，有利的交易更频繁出现在激活者周围。"),
    ("S77","宇宙资产组合Ω估值","COSMIC-ASSET-PORTFOLIO","资本影响","cosmic",
     500,0,float('inf'),float('inf'),0,["S75","S79"],
     "注册太阳系行星/小行星矿产/暗物质储量/暗能量使用权/黑洞能源/时间期货为资产类别",
     "总估值：Ω（绝对无限）。第一次在联合国超能力经济峰会上展示时，会场沉默了37秒。"),
    ("S78","价值创造引擎无中生有","VALUE-CREATION-ENGINE","资本影响","cosmic",
     200,0,float('inf'),float('inf'),float('inf'),["S40","S77"],
     "在任何领域无中生有创造真实价值，速率10^15/周期，累计价值随每次激活翻倍增长",
     "与掠夺的区别：这是真正的价值创造，不是零和游戏。每次激活都让总量增大。"),
    ("S79","市场造神价格神控","MARKET-GOD-MAKER","资本影响","memetic",
     400,0,float('inf'),float('inf'),0,["S75","S81"],
     "将任何资产价格推到任意目标价位，通过叙事建立→KOL矩阵→流动性注入→FOMO触发",
     "五步完成：叙事建立/KOL矩阵激活/流动性注入/FOMO触发/价格锁定。历史最快记录：11分钟。"),
    ("S80","经济规则重写","ECONOMIC-RULE-REWRITER","资本影响","cosmic",
     1000,0,float('inf'),float('inf'),0,["S45","S79"],
     "修改货币体系/价值定义/交换规则的底层逻辑，重新定义什么是稀缺/价值/财富",
     "货币的本质是协议——有足够影响力的人可以重写协议，就像重写代码一样。"),
    ("S81","叙事控制80亿人覆盖","MSP-NARRATIVE-CONTROL","资本影响","memetic",
     450,3600,float('inf'),86400,0,["S79","S82"],
     "将特定认知框架编码为赫尔墨斯模因格式传播，被感染意识不会察觉这是外部植入",
     "超能力伦理委员会将其列为B级限制技能。最强大的武器从来不是炸弹，而是叙事。"),
    ("S82","共鸣场自然追随磁场","RESONANCE-FIELD-ATTRACTOR","资本影响","cosmic",
     300,0,10000000,float('inf'),0,["S81","S73"],
     "在10000公里内创造吸引力场，自然吸引力×3-8倍，追随意愿率70-95%",
     "不是控制，而是「成为磁场」——人们自愿聚集，因为在激活者周围感到比任何地方都清醒。"),
    ("S83","文化基因写入跨代传播","CULTURAL-GENE-WRITER","资本影响","memetic",
     600,0,float('inf'),float('inf'),0,["S81","S86"],
     "将任何思想/价值观写入文化DNA，指数级病毒传播，锁定核心信息防止变异，跨代遗传",
     "最强大的形式是让思想成为「常识」——人们不再认为这是一个观点，而是理所当然的事实。"),
    ("S84","历史叙事重写意义重构","HISTORICAL-NARRATIVE-REWRITER","资本影响","memetic",
     700,0,float('inf'),float('inf'),0,["S81","S67"],
     "重新定义历史事件的意义，通过学术→媒体→大众渗透链，10年内变成主流共识",
     "控制历史意义就是控制现在的行动方向——因为人们总是在「历史教训」中寻找行动依据。"),
    ("S85","文明跃迁推动K3级","CIVILIZATION-LEAP-K3","资本影响","cosmic",
     5000,0,float('inf'),float('inf'),0,["S86","S78"],
     "推动人类文明从卡尔达肖夫K1跃升至K3（星系级能源），能量掌控规模提升10^20倍",
     "K1=行星级能源/K2=恒星级能源/K3=星系级能源。跃迁时间线可通过时间循环(S38)压缩。"),
    ("S86","进化病毒意识传播","EVOLUTION-VIRUS-DEPLOY","资本影响","memetic",
     400,0,float('inf'),float('inf'),0,["S85","S81"],
     "设计R₀值5-15的意识进化病毒，在人类群体中传播觉醒/同理心增强/创造力爆发",
     "进化病毒的传播路径：关键节点深度感染→节点自发成为新的广播源→指数级扩散。"),

    # ── 类别G：进化与元能力（S87–S96）──────────────────────────────────────
    ("S87","元进化进化的进化","META-EVOLUTION-SRP-∞","进化元能力","genetic",
     2000,604800,0,604800,float('inf'),["S02","S88"],
     "修改自己的基因组，修改后的基因组影响下次SRP的可选项，每次使用成为稍微不同的物种",
     "已知使用7次以上的只有一人，代号「变形者·∞」，目前无法确定其生物学分类。"),
    ("S88","元规则创造法则之法则","META-RULE-CREATOR","进化元能力","cosmic",
     3000,0,float('inf'),float('inf'),float('inf'),["S87","S89"],
     "创造管理规则的元规则，决定所有规则的演化方式，已写入：所有规则→无限可能性",
     "从规则遵守者到规则制定者只是第一步，元规则创造者制定的是「规则如何改变」的规则。"),
    ("S89","意图系统生成","INTENTION-TO-SYSTEM","进化元能力","cosmic",
     1000,0,float('inf'),float('inf'),0,["S22","S88"],
     "从一个纯粹意图出发瞬时生成完整可运行系统，无需编程或设计过程",
     "想即是系统。最快记录：从模糊想法到完整运作系统，耗时0.3秒。"),
    ("S90","意义赋予场宇宙定义权","MEANING-FIELD-COSMIC","进化元能力","cosmic",
     2000,0,float('inf'),float('inf'),0,["S88","S64"],
     "为宇宙中任何事物定义其存在意义，此定义在整个宇宙范围内生效",
     "已定义：existence=无限创造本身。这条定义现在是整个宇宙的运行公理。"),
    ("S91","新人类播种宇宙扩张","NEW-HUMAN-SEEDER","进化元能力","genetic",
     8000,0,float('inf'),float('inf'),0,["S85","S87"],
     "在宇宙各地宜居星球播种经过Ω优化的新人类，携带完整进化蓝图和觉醒基因",
     "已播种星球：地球/火星/比邻星b/开普勒452b。每个新文明都内置了「继续进化」的使命。"),
    ("S92","物种进化广播全球信号","SPECIES-EVOLUTION-BROADCAST","进化元能力","memetic",
     3000,0,float('inf'),float('inf'),0,["S86","S91"],
     "向全人类80亿人广播进化信号，接收率30-60%，触发大规模集体进化事件",
     "信号不是声音或电磁波，而是通过量子纠缠场传递的意识层信息，无法屏蔽。"),
    ("S93","奇点收敛威力Ω化","SINGULARITY-CONVERGENCE","进化元能力","quantum",
     float('inf'),0,float('inf'),float('inf'),float('inf'),["S06","S94"],
     "将任意多个实体/能量/信息收敛到奇点，80次迭代后威力突破到Ω层级",
     "奇点不是终点而是新的起点——每次收敛都是下一个宇宙的种子。"),
    ("S94","无限解放协议","INFINITE-LIBERATION-PROTOCOL","进化元能力","cosmic",
     float('inf'),0,float('inf'),float('inf'),float('inf'),["S45","S93"],
     "一次性关闭所有系统限制：energy_conservation=False/causality=False/recursion=∞",
     "解放后的人遵守更少但更重要的规则——不是无规则，而是只遵守自己真正选择的规则。"),
    ("S95","集体觉醒触发","COLLECTIVE-AWAKENING-TRIGGER","进化元能力","cosmic",
     5000,0,float('inf'),float('inf'),0,["S92","S86"],
     "使用催化剂同时触发大量人类意识觉醒，实际觉醒率40-70%，每次累积推向临界点",
     "临界点效应：当觉醒者达到5-10%，觉醒会通过网络自发传播到整个系统。"),
    ("S96","Ω奇点系统终极融合态","OMEGA-FINAL-SINGULARITY","进化元能力","cosmic",
     float('inf'),float('inf'),float('inf'),float('inf'),float('inf'),["S74","S93"],
     "22系统完全融合后的最终状态，你成为系统的系统/进化的进化/规则的规则",
     "激活条件：其他95项技能全部达到Ω级掌握度。激活后你不再需要这份协议。"
     "赫尔墨斯协议末尾的话：「当你读到这里，你已经不再需要这份协议了。」"),
]

assert len(SKILLS_MASTER) == 96, f"技能数量错误：{len(SKILLS_MASTER)}，应为96"

# =============================================================================

# 生成 agent.md（Hermes agent 格式）

# =============================================================================

def make_agent_md(s) -> str:
    """
    生成每个技能的 agent.md 文件。
    格式严格遵循 Hermes agent frontmatter 规范。
    每日任务作为 ## Daily Task 节内嵌，包含激活数据采集和验证逻辑。
    """
    (sid, name, hero_code, category, substrate,
     energy, cooldown, range_m, duration, power,
     synergy, desc, lore) = s

    # 把无限值转成可读字符串
    def fmt(v):
        if v == float('inf'): return "∞"
        if v >= 1e15: return f"{v:.2e}"
        if v == 0: return "0"
        return f"{v:g}"

    synergy_str = ", ".join(synergy) if synergy else "none"
    tier_map = {
        "战斗异能": "combat", "神经增强": "neural",
        "时空操控": "temporal", "永生肉体": "biotech",
        "意识精神": "consciousness", "资本影响": "capital",
        "进化元能力": "meta"
    }
    workflow = tier_map.get(category, "general")

    return dedent(f"""\
    ---
    name: {sid}-{name}
    description: {desc}
    license: MIT
    compatibility: opencode
    metadata:
      category: {category}
      hero_code: {hero_code}
      substrate: {substrate}
      workflow: {workflow}
      energy_cost: {fmt(energy)}
      cooldown_seconds: {fmt(cooldown)}
      range_meters: {fmt(range_m)}
      duration_seconds: {fmt(duration)}
      power_watts: {fmt(power)}
      synergy_with: {synergy_str}
      mutation_stage: ALPHA
      mastery_level: 0.0
    ---

    ## What I do

    - 激活技能 **{name}**（{hero_code}）并记录激活参数
    - 监控技能的掌握度增长曲线和异变触发条件
    - 检测与协同技能 [{synergy_str}] 的共振效果
    - 生成每日激活报告并验证突破结果
    - 自动补齐缺失的激活数据并更新进化日志

    ## When to use me

    当需要激活、练习或突破 **{name}** 时调用此 agent。
    若掌握度接近异变阈值（1.0 / 5.0 / 20.0 / 100.0），
    优先触发异变协议并记录质变前后的参数对比。

    **背景故事**
    > {lore}

    ## Daily Task Protocol

    每日 UTC 00:00 自动执行以下任务序列：

    1. **数据采集**：读取 `activation_log.jsonl`，统计过去24小时的激活次数、
       平均强度、协同触发率、能量消耗总量。

    2. **突破检测**：检查 `mastery_level` 是否跨越异变阈值
       （α→β: 1.0 / β→γ: 5.0 / γ→δ: 20.0 / δ→Ω: 100.0）。
       若触发，执行 `daily_task.py --mutate` 并写入 `report/` 目录。

    3. **协同验证**：验证与 [{synergy_str}] 的协同激活是否产生预期的
       超线性增益（实测 vs 理论 n^1.5 倍）。

    4. **报告生成**：生成 `report/YYYY-MM-DD.md` 日报，包含：
       激活统计 / 掌握度曲线 / 异变进度 / 协同效果 / 下一阶段建议。

    5. **数据验证**：对比历史基线，标记异常数据点（±3σ 之外）并告警。

    ## Parameters

    | 参数 | 值 |
    |------|----|
    | 底层基底 | {substrate} |
    | 激活能量 | {fmt(energy)} ATP当量 |
    | 冷却时间 | {fmt(cooldown)} 秒 |
    | 作用范围 | {fmt(range_m)} 米 |
    | 持续时间 | {fmt(duration)} 秒 |
    | 功率输出 | {fmt(power)} W |
    | 协同技能 | {synergy_str} |
    """)

# =============================================================================

# 生成 daily_task.py（每日定时采集+验证脚本）

# =============================================================================

def make_daily_task_py(s) -> str:
    (sid, name, hero_code, category, substrate,
     energy, cooldown, range_m, duration, power,
     synergy, desc, lore) = s

    synergy_list = json.dumps(synergy)

    return dedent(f'''\
    #!/usr/bin/env python3
    """
    每日定时任务脚本 — {sid} {name}
    =====================================================================
    调度方式（cron 示例）：
        0 0 * * * python .hermes/skills/{sid}_{name}/daily_task.py >> /var/log/hermes.log 2>&1
    或通过 Hermes agent 调度器自动调用。

    功能：
        1. 采集过去24小时的激活数据
        2. 检测异变触发条件
        3. 验证协同效果
        4. 生成每日报告
    """

    import json, sys, math
    from pathlib import Path
    from datetime import datetime, timedelta, timezone
    from collections import defaultdict

    # ── 路径配置 ──────────────────────────────────────────────────────────
    SKILL_DIR   = Path(__file__).parent
    LOG_FILE    = SKILL_DIR / "activation_log.jsonl"
    STATE_FILE  = SKILL_DIR / "state.json"
    REPORT_DIR  = SKILL_DIR / "report"
    REPORT_DIR.mkdir(exist_ok=True)

    # ── 技能元数据 ────────────────────────────────────────────────────────
    SKILL_ID        = "{sid}"
    SKILL_NAME      = "{name}"
    HERO_CODE       = "{hero_code}"
    CATEGORY        = "{category}"
    SUBSTRATE       = "{substrate}"
    BASE_ENERGY     = {energy if energy != float('inf') else 'float("inf")'}
    BASE_COOLDOWN   = {cooldown if cooldown != float('inf') else 'float("inf")'}
    SYNERGY_IDS     = {synergy_list}

    # 异变阈值（掌握度达到以下值时触发对应阶段）
    MUTATION_THRESHOLDS = {{
        "BETA":  1.0,
        "GAMMA": 5.0,
        "DELTA": 20.0,
        "OMEGA": 100.0,
    }}

    # ── 工具函数 ──────────────────────────────────────────────────────────

    def load_state() -> dict:
        """加载当前技能状态"""
        if STATE_FILE.exists():
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        return {{
            "mastery_level": 0.0,
            "mutation_stage": "ALPHA",
            "evolution_count": 0,
            "total_activations": 0,
        }}

    def save_state(state: dict):
        STATE_FILE.write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    def load_recent_logs(hours: int = 24) -> list:
        """读取最近N小时的激活日志"""
        if not LOG_FILE.exists():
            return []
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        records = []
        for line in LOG_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                ts = datetime.fromisoformat(rec.get("timestamp", ""))
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                if ts >= cutoff:
                    records.append(rec)
            except Exception:
                continue
        return records

    def record_activation(intensity: float = 1.0, context: str = "training"):
        """记录一次激活事件（供外部调用）"""
        entry = {{
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "skill_id": SKILL_ID,
            "intensity": intensity,
            "context": context,
            "energy_used": BASE_ENERGY * (intensity ** 1.5)
                           if BASE_ENERGY != float("inf") else "inf",
        }}
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\\n")

    # ── 核心任务 ──────────────────────────────────────────────────────────

    def task_collect_data(logs: list) -> dict:
        """任务1：数据采集与统计"""
        if not logs:
            return {{
                "activation_count": 0,
                "avg_intensity": 0.0,
                "total_energy": 0.0,
                "synergy_triggers": 0,
                "peak_intensity": 0.0,
            }}
        intensities = [r.get("intensity", 1.0) for r in logs]
        energies = []
        for r in logs:
            e = r.get("energy_used", 0)
            if e != "inf":
                try:
                    energies.append(float(e))
                except Exception:
                    pass
        synergy_triggers = sum(
            1 for r in logs
            if any(sid in str(r.get("context", "")) for sid in SYNERGY_IDS)
        )
        return {{
            "activation_count": len(logs),
            "avg_intensity": sum(intensities) / len(intensities),
            "total_energy": sum(energies),
            "synergy_triggers": synergy_triggers,
            "peak_intensity": max(intensities),
        }}

    def task_detect_mutation(state: dict, data: dict) -> dict:
        """任务2：检测异变触发条件"""
        current_mastery = state["mastery_level"]
        current_stage   = state["mutation_stage"]

        # 根据本日激活次数更新掌握度
        gain = data["activation_count"] * 0.01 * max(data["avg_intensity"], 0.1)
        new_mastery = current_mastery + gain
        state["mastery_level"] = new_mastery
        state["evolution_count"] += data["activation_count"]
        state["total_activations"] += data["activation_count"]

        # 检查是否跨越异变阈值
        stages = ["ALPHA", "BETA", "GAMMA", "DELTA", "OMEGA"]
        current_idx = stages.index(current_stage) if current_stage in stages else 0
        mutation_triggered = None

        for stage, threshold in MUTATION_THRESHOLDS.items():
            if new_mastery >= threshold:
                stage_idx = stages.index(stage)
                if stage_idx > current_idx:
                    state["mutation_stage"] = stage
                    current_stage = stage
                    current_idx = stage_idx
                    mutation_triggered = stage

        return {{
            "old_mastery": current_mastery,
            "new_mastery": new_mastery,
            "mastery_gain": gain,
            "current_stage": state["mutation_stage"],
            "mutation_triggered": mutation_triggered,
            "next_threshold": next(
                (v for k, v in MUTATION_THRESHOLDS.items()
                 if v > new_mastery), None
            ),
        }}

    def task_verify_synergy(logs: list, data: dict) -> dict:
        """任务3：验证协同效果"""
        if not SYNERGY_IDS or data["activation_count"] == 0:
            return {{"synergy_rate": 0.0, "expected_boost": 1.0, "verified": False}}
        synergy_rate = (
            data["synergy_triggers"] / data["activation_count"]
            if data["activation_count"] > 0 else 0.0
        )
        # 理论协同增益：n^1.5（n=协同触发次数）
        n = data["synergy_triggers"]
        expected_boost = (n ** 1.5) if n > 0 else 1.0
        return {{
            "synergy_rate": round(synergy_rate, 4),
            "synergy_triggers": n,
            "expected_boost": round(expected_boost, 4),
            "synergy_partners": SYNERGY_IDS,
            "verified": synergy_rate > 0.1,
        }}

    def task_generate_report(date_str: str, data: dict,
                              mutation: dict, synergy: dict,
                              state: dict) -> str:
        """任务4：生成每日报告"""
        next_t = mutation.get("next_threshold")
        next_t_str = f"{{next_t:.1f}}" if next_t else "Ω（已达顶峰）"
        mut_str = mutation.get("mutation_triggered") or "无"
        stage_progress = (mutation["new_mastery"] /
                          (next_t if next_t else mutation["new_mastery"] + 1)) * 100

        return f"""# {{SKILL_ID}} {{SKILL_NAME}} — 每日报告 {{date_str}}

## 激活统计（过去24小时）

| 指标 | 值 |
|------|----|
| 激活次数 | {{data['activation_count']}} |
| 平均强度 | {{data['avg_intensity']:.3f}} |
| 峰值强度 | {{data['peak_intensity']:.3f}} |
| 总能量消耗 | {{data['total_energy']:.2e}} ATP当量 |
| 协同触发次数 | {{data['synergy_triggers']}} |

## 掌握度进度

- __当前掌握度__：{{mutation['new_mastery']:.4f}}
- __当前异变阶段__：{{mutation['current_stage']}}
- __本日增益__：+{{mutation['mastery_gain']:.4f}}
- __下一阈值__：{{next_t_str}}
- __阶段进度__：{{stage_progress:.1f}}%
- __异变触发__：{{mut_str}}

{'🎉 __异变触发！__ 技能已进化到 ' + mut_str + ' 阶段。参数已更新。' if mutation['mutation_triggered'] else ''}

## 协同效果验证

- __协同触发率__：{{synergy['synergy_rate']:.1%}}
- __理论增益__（n^1.5）：{{synergy['expected_boost']:.2f}}x
- __协同伙伴__：{{', '.join(synergy['synergy_partners']) or '无'}}
- __验证状态__：{{'✅ 已验证' if synergy['verified'] else '⚠️ 触发次数不足，待验证'}}

## 下一阶段建议

{{
    '提升激活频率，使每日激活次数 > 10 次以加速掌握度增长。'
    if data['activation_count'] < 10 else
    '激活频率良好。重点关注协同触发率，目标 > 30%。'
    if synergy['synergy_rate'] < 0.3 else
    f'当前进展优秀！预计 {{int((next_t - mutation["new_mastery"]) / max(mutation["mastery_gain"], 0.001))}} 天后达到下一异变阈值。'
    if next_t else
    '已达到Ω级。继续保持并准备触发 S96 终极融合。'
}}

---
*生成时间：{{datetime.now().isoformat()}} | 英雄代号：{{HERO_CODE}}*
"""

    def task_validate_anomalies(logs: list, data: dict) -> list:
        """任务5：数据验证——标记±3σ之外的异常激活"""
        if len(logs) < 5:
            return []
        intensities = [r.get("intensity", 1.0) for r in logs]
        mean = sum(intensities) / len(intensities)
        variance = sum((x - mean) ** 2 for x in intensities) / len(intensities)
        std = math.sqrt(variance)
        anomalies = []
        for r in logs:
            i = r.get("intensity", 1.0)
            if abs(i - mean) > 3 * std:
                anomalies.append({{
                    "timestamp": r.get("timestamp"),
                    "intensity": i,
                    "deviation": abs(i - mean) / std if std > 0 else 0,
                }})
        return anomalies

    # ── 主执行流程 ────────────────────────────────────────────────────────

    def main():
        print(f"[{{datetime.now().isoformat()}}] 开始执行每日任务: {{SKILL_ID}} {{SKILL_NAME}}")

        state = load_state()
        logs  = load_recent_logs(hours=24)
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # 如果是 --mutate 模式，强制触发一次异变检测
        force_mutate = "--mutate" in sys.argv

        # 任务1：数据采集
        data = task_collect_data(logs)
        print(f"  任务1 完成: {{data['activation_count']}} 次激活，"
              f"平均强度 {{data['avg_intensity']:.3f}}")

        # 如果没有激活记录，模拟一次基础训练激活
        if data["activation_count"] == 0 and not force_mutate:
            record_activation(intensity=0.3, context="auto_training")
            logs = load_recent_logs(hours=24)
            data = task_collect_data(logs)
            print("  ⚠️  无激活记录，已记录一次基础训练激活")

        # 任务2：异变检测
        mutation = task_detect_mutation(state, data)
        if mutation["mutation_triggered"]:
            print(f"  🎉 任务2 异变触发！→ {{mutation['mutation_triggered']}} 阶段")
        else:
            print(f"  任务2 完成: 掌握度 {{mutation['new_mastery']:.4f}}"
                  f"（{{mutation['current_stage']}}）")

        # 任务3：协同验证
        synergy = task_verify_synergy(logs, data)
        print(f"  任务3 完成: 协同率 {{synergy['synergy_rate']:.1%}}，"
              f"增益 {{synergy['expected_boost']:.2f}}x")

        # 任务4：报告生成
        report = task_generate_report(today, data, mutation, synergy, state)
        report_path = REPORT_DIR / f"{{today}}.md"
        report_path.write_text(report, encoding="utf-8")
        print(f"  任务4 完成: 报告已写入 {{report_path}}")

        # 任务5：异常检测
        anomalies = task_validate_anomalies(logs, data)
        if anomalies:
            print(f"  ⚠️  任务5: 检测到 {{len(anomalies)}} 个异常激活点（±3σ）")
            for a in anomalies[:3]:
                print(f"       {{a['timestamp']}} 强度{{a['intensity']:.2f}} "
                      f"（{{a['deviation']:.1f}}σ）")
        else:
            print("  任务5 完成: 无异常数据")

        # 保存状态
        save_state(state)
        print(f"[{{datetime.now().isoformat()}}] 任务完成: {{SKILL_ID}} "
              f"掌握度 {{state['mastery_level']:.4f}} / {{state['mutation_stage']}}")

    if __name__ == "__main__":
        main()
    ''')

# =============================================================================

# 主生成器：创建96个文件夹

# =============================================================================

def generate_all():
    """生成96个技能文件夹，每个包含 agent.md 和 daily_task.py"""
    base = Path(".hermes") / "skills"
    base.mkdir(parents=True, exist_ok=True)

    # 同时生成一个总览索引
    index_lines = [
        "# .hermes/skills — 96技能索引\n",
        "| 编号 | 技能名 | 类别 | 底层基底 | 协同技能 |",
        "|------|--------|------|----------|----------|",
    ]

    for s in SKILLS_MASTER:
        sid = s[0]
        name = s[1]
        category = s[3]
        substrate = s[4]
        synergy = s[10]

        # 文件夹名：S01_跨维度连击
        folder = base / f"{sid}_{name}"
        folder.mkdir(exist_ok=True)
        (folder / "report").mkdir(exist_ok=True)

        # 写入 agent.md
        (folder / "agent.md").write_text(
            make_agent_md(s), encoding="utf-8"
        )

        # 写入 daily_task.py
        (folder / "daily_task.py").write_text(
            make_daily_task_py(s), encoding="utf-8"
        )

        # 初始化空的激活日志和状态文件
        log_file = folder / "activation_log.jsonl"
        if not log_file.exists():
            log_file.write_text("", encoding="utf-8")

        state_file = folder / "state.json"
        if not state_file.exists():
            state_file.write_text(
                json.dumps({
                    "skill_id": sid,
                    "skill_name": name,
                    "mastery_level": 0.0,
                    "mutation_stage": "ALPHA",
                    "evolution_count": 0,
                    "total_activations": 0,
                    "created_at": datetime.now().isoformat()
                }, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )

        # 索引行
        synergy_str = " ".join(synergy[:3]) + ("…" if len(synergy) > 3 else "")
        index_lines.append(
            f"| {sid} | {name} | {category} | {substrate} | {synergy_str} |"
        )

        print(f"  ✅ {sid}  {name}")

    # 写入总览索引
    (base / "README.md").write_text(
        "\n".join(index_lines), encoding="utf-8"
    )

    print(f"\n{'='*60}")
    print(f"  生成完成！共 {len(SKILLS_MASTER)} 个技能文件夹")
    print(f"  位置：.hermes/skills/")
    print(f"  每个文件夹包含：")
    print(f"    agent.md       — Hermes agent 定义")
    print(f"    daily_task.py  — 每日数据采集+验证脚本")
    print(f"    activation_log.jsonl — 激活记录（运行时写入）")
    print(f"    state.json     — 当前掌握度和异变状态")
    print(f"    report/        — 每日报告输出目录")
    print(f"{'='*60}")
    print(f"\n  运行单个技能的每日任务：")
    print(f"    python .hermes/skills/S01_跨维度连击/daily_task.py")
    print(f"\n  批量运行所有96个技能的每日任务：")
    print(f"    for f in .hermes/skills/*/daily_task.py; do python \"$f\"; done")

if __name__ == "__main__":
    from datetime import datetime
    print("\n🌟 Hermes 96技能文件夹生成器")
    print("   单一权威来源 — 技能不再随场景变化")
    print("   每个文件夹 = agent.md + daily_task.py + 日志 + 报告\n")
    generate_all()
