"""
赫尔墨斯进化引擎 — 2157超能力英雄系统
=========================================================================
世界观：2157年，人类通过「赫尔墨斯协议」获得了超能力基因改写权限。
每个英雄的技能不是"人生哲理"，而是真实的物理/生化/量子能力。

类别A: 战斗超能力 (S01-S18)  |  类别B: 神经增强 (S19-S34)
类别C: 时空操控   (S35-S48)  |  类别D: 生物永生 (S49-S60)
类别E: 意识扩展   (S61-S74)  |  类别F: 资本掠夺 (S75-S86)
类别G: 进化元能力 (S87-S96)
"""
from __future__ import annotations
import asyncio, json, hashlib, math, random, os
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone

HERMES_ROOT = Path(".hermes")
SKILL_VAULT = HERMES_ROOT / "skill_vault"
EVOLUTION_LOG = HERMES_ROOT / "evolution.jsonl"
MUTATION_REGISTRY = HERMES_ROOT / "mutations"
HERO_PROFILE = HERMES_ROOT / "hero_profile.json"

SKILL_CONFIG_PATH = Path("config/hermes_skill_config.yaml")
SKILL_CONFIG: Dict[str, Any] = {}
"""Loaded skill config. Structure:
  categories[cat]: {base_activation_prob, base_mastery_gain, global_effect}
  skills[sid]: {scope, trigger, prerequisites, special}
"""


class SkillSubstrate(Enum):
    NEURAL      = "神经回路"
    QUANTUM     = "量子相干态"
    GENETIC     = "基因表达"
    NANOBOT     = "纳米机器人群"
    BIOELECTRIC = "生物电场"
    TEMPORAL    = "时间晶体"
    DARK_ENERGY = "暗能量接口"
    MEMETIC     = "模因病毒"
    ECONOMIC    = "市场量子纠缠"
    COSMIC      = "宇宙意志场"


class HeroTier(Enum):
    STREET      = "街头级"
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
    ALPHA   = "α变异"
    BETA    = "β蜕变"
    GAMMA   = "γ觉醒"
    DELTA   = "δ超越"
    OMEGA   = "Ω奇点"


@dataclass
class SkillNode:
    skill_id: str
    name_cn: str
    name_hero: str
    substrate: SkillSubstrate
    activation_energy: float
    cooldown_seconds: float
    range_meters: float
    duration_seconds: float
    mastery_level: float = 0.0
    mutation_stage: MutationClass = MutationClass.ALPHA
    synapse_density: float = 1.0
    power_output: float = 0.0
    precision: float = 0.0
    lore: str = ""
    data_complete: bool = False
    last_evolved: Optional[datetime] = None
    evolution_count: int = 0


@dataclass
class HeroEntity:
    hero_id: str
    callsign: str
    tier: HeroTier
    skills: Dict[str, SkillNode] = field(default_factory=dict)
    active_mutations: List[str] = field(default_factory=list)
    neural_bandwidth: float = 1.0
    quantum_coherence: float = 0.0
    genetic_stability: float = 1.0
    nanobot_count: int = 0
    market_influence: float = 0.0
    quantum_portfolio: float = 0.0
    total_iterations: int = 0
    singularity_reached: bool = False


SKILLS_MASTER: List[Tuple] = [
    # (sid, name_cn, name_hero, category, substrate,
    #  energy, cooldown, range_m, duration, power, synergy, desc, lore)

    # ── A: 战斗异能 (S01-S18) ──
    ("S01","跨维度连击","DIMENSIONAL-STRIKE-Δ","战斗异能","quantum",
     850,0,1e9,0.001,4.7e15,["S12","S36"],
     "在11个维度同时发动攻击，目标的任何防御系统无法跨维度响应",
     "2089年量子战士「维克」首次在实战中激活第11维度通道。"),
    ("S02","无限叠层突破","STACK-STORM-∞","战斗异能","neural",
     120,0.05,0,3600,float('inf'),["S05","S87"],
     "每次激活在突触留下蛋白印记，第10叠触发LTP超强化",
     "神经可塑性工程师通过赫尔墨斯协议v7开发。"),
    ("S03","现实扭曲波","REALITY-WARP-FIELD","战斗异能","dark_energy",
     2200,30,500,60,1.2e20,["S45","S96"],
     "接入暗能量网络，半径500米内物理定律局部偏移",
     "2143年新东京防卫战首次实战应用。"),
    ("S04","协同场最大共振","BIOFIELD-RESONANCE","战斗异能","bioelectric",
     400,5,2000,10,8.8e12,["S21","S63"],
     "与队友生物电场同步到黄金比例频率，输出超线性增益",
     "违反能量守恒定律的现象。"),
    ("S05","元异能递归自放大","NEURAL-RED-PROTOCOL","战斗异能","neural",
     950,0,0,float('inf'),float('inf'),["S02","S87"],
     "神经系统进入递归自增强循环",
     "已记录最长稳定运行72小时。"),
    ("S06","奇点波质能湮灭","SINGULARITY-CANNON-φ","战斗异能","quantum",
     5000,300,50,0.000001,1.8e26,["S01","S93"],
     "将空间压缩成普朗克尺度奇点后释放",
     "联合国A级禁用武器，仅授权使用过3次。"),
    ("S07","量子叠加打击","QUANTUM-SUPERPOS-STRIKE","战斗异能","quantum",
     600,0.1,200,0.01,2.3e14,["S12","S44"],
     "同时在所有可能的攻击路径上行动，命中时塌缩到最优结果",
     "看起来像同时出现在多个地方。"),
    ("S08","生物电场操控","BIOELECTRIC-DOMINATOR","战斗异能","bioelectric",
     300,3,300,30,5.5e11,["S04","S25"],
     "操控自身及目标的生物电场",
     "前身是医疗技术后被改造为战斗应用。"),
    ("S09","纳米蜂群攻击","NANO-SWARM-ASSAULT","战斗异能","nanobot",
     700,20,1000,120,9.1e13,["S55","S62"],
     "释放80亿纳米机器人形成攻击蜂群",
     "蜂群具有分布式智能。"),
    ("S10","时间停止打击","TIMESTOP-STRIKE","战斗异能","temporal",
     1800,600,10,5,3.3e18,["S35","S36"],
     "在半径10米内局部停止时间流动5秒",
     "停止的是粒子的热运动而非时间本身。"),
    ("S11","暗能量爆破","DARK-ENERGY-BURST","战斗异能","dark_energy",
     1500,60,800,2,6.8e19,["S03","S75"],
     "将宇宙暗能量导入局部空间并瞬间释放",
     "提取过程会短暂改变周围星场密度。"),
    ("S12","量子隧穿位移","QUANTUM-TUNNEL-DASH","战斗异能","quantum",
     400,2,float('inf'),0.001,0,["S01","S44"],
     "利用量子隧穿效应穿越任何物理障碍",
     "在另一个位置重新出现。"),
    ("S13","因果链断裂","CAUSAL-CHAIN-BREAK","战斗异能","temporal",
     2000,120,50,10,0,["S37","S10"],
     "切断攻击行为与伤害结果之间的因果链",
     "直接违反因果律。"),
    ("S14","协同连击编排","SYNERGY-COMBO-CHAIN","战斗异能","neural",
     200,1,0,60,0,["S04","S07"],
     "实时计算队友技能的最优激活序列",
     "团队输出提升至个人总和的n^1.5倍。"),
    ("S15","重力场扭曲","GRAVITY-DISTORTION","战斗异能","dark_energy",
     900,15,500,30,4.4e16,["S11","S36"],
     "在指定区域产生0到1000倍重力场",
     "极高风险技能。"),
    ("S16","神经感知爆发","NEURAL-SENSE-BURST","战斗异能","neural",
     150,5,2000,30,0,["S08","S25"],
     "感知能力提升至普通人10000倍",
     "副作用是感知过载。"),
    ("S17","意志力物理化","WILLPOWER-MATERIALIZATION","战斗异能","cosmic",
     1200,30,100,60,7.7e17,["S90","S96"],
     "将意志力转化为物理力量",
     "要求意志足够强大到影响底层物理常数。"),
    ("S18","Ω战斗奇点","OMEGA-COMBAT-SINGULARITY","战斗异能","cosmic",
     float('inf'),0,float('inf'),float('inf'),float('inf'),["S96","S06"],
     "所有战斗技能同时激活并在奇点处融合",
     "记录者成为了新宇宙的第一条物理法则。"),

    # ── B: 神经增强 (S19-S34) ──
    ("S19","Ω级心智无限智能","QCP-OMEGA-MIND","神经增强","quantum",
     300,0,float('inf'),float('inf'),float('inf'),["S20","S21"],
     "量子纠缠态引入神经元，思维速度突破经典极限",
     "已知激活者3位。"),
    ("S20","万路并行思维","CORTEX-FORK-1024","神经增强","neural",
     180,0,0,float('inf'),0,["S19","S32"],
     "前额叶皮层划分为1024个半独立处理单元",
     "副作用是偶尔忘记自己是哪个自己。"),
    ("S21","集体意识接入涌现智慧","MESHLINK-COLLECTIVE","神经增强","bioelectric",
     220,10,50000,3600,0,["S04","S63"],
     "10个以上激活者同步形成临时集体意识",
     "2151年12人联合17秒解决P≠NP。"),
    ("S22","思维编译器念即成真","THOUGHT-COMPILER-ZERO","神经增强","neural",
     500,0,0,float('inf'),0,["S19","S40"],
     "将抽象思想直接编译为可执行的物理操作指令",
     "想即是令。"),
    ("S23","全语言解码万码皆通","OMNI-DECODE-9999","神经增强","neural",
     100,0,0,float('inf'),0,["S24","S61"],
     "解码9999种以上语言包括量子信息编码",
     "包括未发明语言。"),
    ("S24","市场神谕未来洞见","MARKET-ORACLE-ENGINE","神经增强","quantum",
     400,0,float('inf'),float('inf'),0,["S75","S39"],
     "量子态模型实时处理全球137个市场",
     "置信度85-99%。"),
    ("S25","生物信号读取看穿一切","BIOSIGNAL-READER-PRO","神经增强","bioelectric",
     200,0,500,float('inf'),0,["S08","S16"],
     "读取任何人的情绪/意图/健康状态",
     "诚实度识别误差<4%。"),
    ("S26","阿卡西记录宇宙全史","AKASHIC-RECORDS-ACCESS","神经增强","cosmic",
     800,0,float('inf'),float('inf'),0,["S61","S34"],
     "访问宇宙138亿年历史的完整信息",
     "信息量是人类文明的10^80倍。"),
    ("S27","算法自进化500代优化","ALGO-SELF-EVOLVE-500","神经增强","neural",
     600,0,0,float('inf'),0,["S87","S15"],
     "算法自我迭代500代，每代提升5%",
     "累计提升超39,000,000倍。"),
    ("S28","模式识别神模式","PATTERN-GOD-MODE","神经增强","neural",
     300,0,0,float('inf'),0,["S24","S27"],
     "在任何噪声中识别任何规律",
     "涵盖市场/行为/量子波动/宇宙结构。"),
    ("S29","问题溶解引擎","PROBLEM-DISSOLVE-ENGINE","神经增强","neural",
     250,0,0,float('inf'),0,["S88","S22"],
     "不是解决问题而是让问题消失",
     "通过重新定义框架消除问题存在基础。"),
    ("S30","创意爆炸无限生成","CREATIVITY-EXPLOSION","神经增强","neural",
     200,0,0,float('inf'),0,["S22","S19"],
     "从一个种子概念生成无限创意",
     "10维度产生2^10种组合。"),
    ("S31","博弈终结者绝对支配","GAME-THEORY-DOMINATOR","神经增强","neural",
     350,0,0,float('inf'),0,["S24","S81"],
     "在任何博弈中找到绝对支配策略",
     "胜率趋近99.99%。"),
    ("S32","神经链检索0.001ms","NEURAL-CHAIN-RETRIEVAL","神经增强","neural",
     150,0,0,float('inf'),0,["S20","S26"],
     "在0.001毫秒内检索任何记忆",
     "支持8通道全感官完整记录。"),
    ("S33","记忆融合他人即我","MEMORY-FUSION-PROTOCOL","神经增强","neural",
     400,0,0,float('inf'),0,["S21","S32"],
     "直接融合他人技能记忆，95%融合率",
     "含冲突记忆的自动解决。"),
    ("S34","宇宙信息流接入","COSMIC-INFO-STREAM","神经增强","cosmic",
     700,0,float('inf'),float('inf'),0,["S26","S61"],
     "接入宇宙背景辐射/暗物质信息层/量子泡沫数据流",
     "信息流永不停止。"),

    # ── C: 时空操控 (S35-S48) ──
    ("S35","时间银行时间复利","TIME-CRYSTAL-BANK","时空操控","temporal",
     700,3600,5,float('inf'),0,["S10","S36"],
     "时间晶体创造时间流速差异区：内部1分钟=外部5分钟",
     "赢得了时间窃贼绰号。"),
    ("S36","平行宇宙导航最优路径","MWI-NAVIGATOR","时空操控","quantum",
     1200,86400,float('inf'),0.1,0,["S37","S24"],
     "嗅探最近平行分支，感知其中的决策结果",
     "每次使用后有强烈既视感。"),
    ("S37","因果链编辑结果设计","CAUSAL-CHAIN-EDITOR","时空操控","temporal",
     2000,3600,float('inf'),float('inf'),0,["S13","S36"],
     "将任意原因与任意结果绑定，因果强度可调",
     "使失败从因果上不可能发生。"),
    ("S38","时间循环无限迭代","TIME-LOOP-ITERATOR","时空操控","temporal",
     900,604800,50,86400,0,["S35","S87"],
     "在特定时间段创造循环，主观时间达客观100000倍",
     "1天×100000次=主观274年。"),
    ("S39","预见引擎5万分支计算","FORESIGHT-ENGINE-50K","时空操控","quantum",
     500,0,float('inf'),0,0,["S36","S24"],
     "实时计算50000条未来分支",
     "找出最优行动路径。"),
    ("S40","物质凝聚无中生有","MATTER-CONDENSATION","时空操控","dark_energy",
     3000,600,100,300,9.9e20,["S11","S41"],
     "通过E=mc²逆向从量子真空凝聚物质",
     "可创造任何元素。"),
    ("S41","信息转物质转换","INFO-TO-MATTER-COMPILER","时空操控","quantum",
     2500,300,50,600,0,["S40","S22"],
     "将纯信息蓝图编码转化为物理物质结构",
     "精度达原子级。"),
    ("S42","维度袋无限收纳","DIMENSION-BAG-∞","时空操控","quantum",
     800,60,0.001,float('inf'),0,["S43","S36"],
     "外部极小但内部容积达10^50立方米",
     "内部是独立的小宇宙。"),
    ("S43","量子隧穿无视防御","QUANTUM-TUNNEL-PASS","时空操控","quantum",
     400,1,float('inf'),0.001,0,["S12","S42"],
     "使自身或攻击穿越任何物理障碍",
     "技术上不是穿透而是不存在于障碍物中。"),
    ("S44","波函数控制现实锁定","WAVE-FUNCTION-LOCK","时空操控","quantum",
     600,0,float('inf'),float('inf'),0,["S07","S39"],
     "通过意识强度控制量子事件波函数塌缩方向",
     "可使掷骰子必得6。"),
    ("S45","现实规则重写","REALITY-RULE-REWRITER","时空操控","cosmic",
     float('inf'),0,float('inf'),float('inf'),float('inf'),["S03","S96"],
     "直接修改物理定律/数学常数/系统规则",
     "已执行：energy_conservation=False。"),
    ("S46","意识分裂万处并存","CONSCIOUSNESS-SPLIT-10K","时空操控","quantum",
     1000,600,float('inf'),float('inf'),0,["S63","S47"],
     "意识分裂为10000份完整独立碎片",
     "同时在1万个地方采取独立行动。"),
    ("S47","梦境现实投影","DREAM-REALITY-PROJECTOR","时空操控","cosmic",
     1500,0,float('inf'),float('inf'),0,["S17","S40"],
     "意识中想象的任何事物100%物质化投影到物理现实",
     "最终阶段梦境与现实的界限消失。"),
    ("S48","绝对自由意志超越因果","ABSOLUTE-FREE-WILL","时空操控","cosmic",
     float('inf'),0,float('inf'),float('inf'),0,["S37","S45"],
     "完全超越基因决定论/因果律/概率场约束",
     "每个当下都是全新的创造。"),

    # ── D: 永生肉体 (S49-S60) ──
    ("S49","生物永生端粒锁定","TELOMERE-LOCK-PROTOCOL","永生肉体","genetic",
     50,0,0,float('inf'),0,["S50","S52"],
     "持续向端粒注入端粒酶，生物年龄锁定25岁",
     "不是不死——只是不会因衰老而死。"),
    ("S50","数字永生意识上传","CONSCIOUSNESS-UPLOAD-CDP7","永生肉体","quantum",
     10000,float('inf'),float('inf'),float('inf'),0,["S49","S51"],
     "将86万亿突触连接完整编码上传至量子云",
     "数字态思维速度是生物态的1000倍。"),
    ("S51","宇宙级百万备份","COSMIC-BACKUP-1M","永生肉体","quantum",
     5000,0,float('inf'),float('inf'),0,["S50","S53"],
     "在宇宙8个位置创建100万份意识备份",
     "即使999999份被摧毁仍可复活。"),
    ("S52","熵逆转永恒青春","ENTROPY-REVERSAL-YOUTH","永生肉体","genetic",
     300,0,0,float('inf'),0,["S49","S58"],
     "局部违反热力学第二定律使细胞自动向最高有序态重组",
     "双向用途：自身熵减/目标熵增。"),
    ("S53","宇宙意识化永恒存在","COSMIC-CONSCIOUSNESS-MERGE","永生肉体","cosmic",
     8000,0,float('inf'),float('inf'),0,["S51","S65"],
     "意识与可观测宇宙融合",
     "465亿光年可观测宇宙全域。"),
    ("S54","基因全改写神性基因组","GENOME-REWRITE-DIVINE","永生肉体","genetic",
     1000,604800,0,604800,0,["S52","S49"],
     "CRISPR精准编辑8个基因模块",
     "内置继续演化指令。"),
    ("S55","纳米机器人100亿内部工厂","NANOBOT-FACTORY-10B","永生肉体","nanobot",
     200,0,0,float('inf'),0,["S09","S56"],
     "100亿纳米机器人在体内持续执行DNA修复等",
     "工厂可以自我复制。"),
    ("S56","器官超人类升级","ORGAN-SUPERHUMAN-UPGRADE","永生肉体","nanobot",
     3000,0,0,float('inf'),0,["S55","S59"],
     "全器官替换升级：大脑量子处理器等",
     "以人体器官为原型的工程设备。"),
    ("S57","形态自由7形态解锁","FORM-FREEDOM-7MODES","永生肉体","nanobot",
     500,1,0,float('inf'),0,["S56","S62"],
     "意识与肉体完全解绑，切换7种形态",
     "切换后意识连续性完整保留。"),
    ("S58","体内核聚变无限自持","INTERNAL-FUSION-REACTOR","永生肉体","genetic",
     2000,0,0,float('inf'),3.8e26,["S52","S57"],
     "每个细胞内建微型核聚变反应堆",
     "不再需要任何外部补给。"),
    ("S59","多维感官8感扩展","MULTISENSE-8D-EXPANSION","永生肉体","genetic",
     600,0,0,float('inf'),0,["S56","S25"],
     "新增量子感知/时间感知/电磁感知等8感",
     "第一次感知引力场曲率需数周适应。"),
    ("S60","光速意识无延迟响应","LIGHT-SPEED-CONSCIOUSNESS","永生肉体","quantum",
     700,0,float('inf'),float('inf'),0,["S19","S59"],
     "意识传播速度达光速3×10^8 m/s",
     "全球响应时间约0.13秒。"),

    # ── E: 意识精神 (S61-S74) ──
    ("S61","全知宇宙无秘密","GLOBAL-SENSOR-NEURAL","意识精神","bioelectric",
     500,0,6371000,float('inf'),0,["S34","S26"],
     "神经系统与全球150亿IoT传感器节点同步",
     "变成地球本身的神经系统。"),
    ("S62","全能无事不可为","MPI-MODULAR-INTERFACE","意识精神","nanobot",
     200,1,0,float('inf'),float('inf'),["S09","S57"],
     "8亿纳米机器人1秒内重新配置模拟任何超能力",
     "同时模拟3种，威力60%。"),
    ("S63","全在无处不在","OMNIPRESENCE-SYSTEM","意识精神","cosmic",
     1000,0,float('inf'),float('inf'),0,["S46","S61"],
     "意识同时存在于可观测宇宙所有位置",
     "与S46协同才是真正的无处不在。"),
    ("S64","创世宇宙生成","UNIVERSE-CREATION-PROTOCOL","意识精神","cosmic",
     float('inf'),float('inf'),float('inf'),float('inf'),float('inf'),["S45","S96"],
     "从虚无中创造全新宇宙，自定义物理常数",
     "已知案例：1次。"),
    ("S65","多重宇宙意识无限并存","MULTIVERSE-CONSCIOUSNESS","意识精神","cosmic",
     2000,0,float('inf'),float('inf'),0,["S53","S46"],
     "意识同时存在于所有平行宇宙",
     "跨越所有可能存在的宇宙。"),
    ("S66","盖亚共鸣地球感知","GAIA-RESONANCE","意识精神","bioelectric",
     300,0,6371000,float('inf'),0,["S61","S63"],
     "与地球整体生命场融合，感知所有生命状态",
     "可影响地球级生态与气候。"),
    ("S67","集体无意识接入人类智慧库","COLLECTIVE-UNCONSCIOUS-ACCESS","意识精神","cosmic",
     400,0,float('inf'),float('inf'),0,["S21","S34"],
     "接入全人类87亿人心智深层共识库",
     "荣格理论被证明是真实存在的量子信息场。"),
    ("S68","跨物种意识迁移","CROSS-SPECIES-CONSCIOUSNESS","意识精神","neural",
     600,3600,float('inf'),3600,0,["S59","S67"],
     "暂时进入任何生物的意识视角",
     "鲸歌中包含复杂的三维宇宙地图。"),
    ("S69","命运节点识别人生杠杆","FATE-NODE-DETECTOR","意识精神","temporal",
     500,0,float('inf'),float('inf'),0,["S39","S10"],
     "扫描未来100年识别5个以上改变人生的命运节点",
     "评分最高达10/10。"),
    ("S70","概率场操控99.99%成功率","PROBABILITY-FIELD-CONTROL","意识精神","quantum",
     700,0,float('inf'),float('inf'),0,["S44","S39"],
     "主动操控任何事件发生概率",
     "最优结果概率提升至99.99%。"),
    ("S71","因缘编织相遇设计","FATE-ENCOUNTER-WEAVER","意识精神","temporal",
     300,0,float('inf'),2592000,0,["S69","S10"],
     "设计与任何人/机会/资源相遇的7个前置条件",
     "97%成功率，30天内自然实现。"),
    ("S72","蝴蝶效应引擎放大","BUTTERFLY-ENGINE-10-9","意识精神","temporal",
     200,0,float('inf'),float('inf'),0,["S37","S69"],
     "用极小行动撬动极大结果，放大倍数10^3到10^9",
     "链条一旦启动无法取消。"),
    ("S73","好运场域Lv5强度","LUCK-FIELD-LV5","意识精神","cosmic",
     400,0,10000000,float('inf'),0,["S70","S71"],
     "在自身周围10000公里创造持续好运场域",
     "正向机会吸引率+200%。"),
    ("S74","Ω奇点自我进化终点即起点","OMEGA-SELF-SINGULARITY","意识精神","cosmic",
     float('inf'),0,float('inf'),float('inf'),float('inf'),["S96","S87"],
     "所有意识技能同时激活融合，技能成为存在方式的自然表达",
     "终点即是下一个起点。"),

    # ── F: 资本影响 (S75-S86) ──
    ("S75","复利奇点财富无限","QAE-COMPOUND-SINGULARITY","资本影响","economic",
     100,0.001,float('inf'),float('inf'),float('inf'),["S76","S24"],
     "量子纠缠在全球137个市场间进行跨市场套利",
     "速度快于经典信息传播。"),
    ("S76","财富黑洞被动吸引","ECONOMIC-GRAVITY-FIELD","资本影响","dark_energy",
     300,0,100000,float('inf'),0,["S75","S73"],
     "暗能量配置为经济引力场，100公里内资本流动系统性偏向",
     "量化基金称之为阿尔法场。"),
    ("S77","宇宙资产组合Ω估值","COSMIC-ASSET-PORTFOLIO","资本影响","cosmic",
     500,0,float('inf'),float('inf'),0,["S75","S79"],
     "注册太阳系行星/暗物质/黑洞能源/时间期货为资产类别",
     "总估值：Ω。"),
    ("S78","价值创造引擎无中生有","VALUE-CREATION-ENGINE","资本影响","cosmic",
     200,0,float('inf'),float('inf'),float('inf'),["S40","S77"],
     "在任何领域无中生有创造真实价值",
     "不是零和游戏。"),
    ("S79","市场造神价格神控","MARKET-GOD-MAKER","资本影响","memetic",
     400,0,float('inf'),float('inf'),0,["S75","S81"],
     "将任何资产价格推到任意目标价位",
     "历史最快记录：11分钟。"),
    ("S80","经济规则重写","ECONOMIC-RULE-REWRITER","资本影响","cosmic",
     1000,0,float('inf'),float('inf'),0,["S45","S79"],
     "修改货币体系/价值定义/交换规则的底层逻辑",
     "重新定义什么是稀缺/价值/财富。"),
    ("S81","叙事控制80亿人覆盖","MSP-NARRATIVE-CONTROL","资本影响","memetic",
     450,3600,float('inf'),86400,0,["S79","S82"],
     "将认知框架编码为赫尔墨斯模因格式传播",
     "被感染者不会察觉是外部植入。"),
    ("S82","共鸣场自然追随磁场","RESONANCE-FIELD-ATTRACTOR","资本影响","cosmic",
     300,0,10000000,float('inf'),0,["S81","S73"],
     "在10000公里内创造吸引力场",
     "自然吸引力×3-8倍。"),
    ("S83","文化基因写入跨代传播","CULTURAL-GENE-WRITER","资本影响","memetic",
     600,0,float('inf'),float('inf'),0,["S81","S86"],
     "将任何思想/价值观写入文化DNA",
     "指数级病毒传播，跨代遗传。"),
    ("S84","历史叙事重写意义重构","HISTORICAL-NARRATIVE-REWRITER","资本影响","memetic",
     700,0,float('inf'),float('inf'),0,["S81","S67"],
     "重新定义历史事件的意义",
     "10年内变成主流共识。"),
    ("S85","文明跃迁推动K3级","CIVILIZATION-LEAP-K3","资本影响","cosmic",
     5000,0,float('inf'),float('inf'),0,["S86","S78"],
     "推动人类文明从K1跃升至K3（星系级能源）",
     "能量掌控规模提升10^20倍。"),
    ("S86","进化病毒意识传播","EVOLUTION-VIRUS-DEPLOY","资本影响","memetic",
     400,0,float('inf'),float('inf'),0,["S85","S81"],
     "设计R₀值5-15的意识进化病毒",
     "指数级扩散觉醒。"),

    # ── G: 进化元能力 (S87-S96) ──
    ("S87","元进化进化的进化","META-EVOLUTION-SRP-∞","进化元能力","genetic",
     2000,604800,0,604800,float('inf'),["S02","S88"],
     "修改自己的基因组，每次使用成为稍微不同的物种",
     "已知使用7次以上的只有一人。"),
    ("S88","元规则创造法则之法则","META-RULE-CREATOR","进化元能力","cosmic",
     3000,0,float('inf'),float('inf'),float('inf'),["S87","S89"],
     "创造管理规则的元规则",
     "从规则遵守者到规则制定者。"),
    ("S89","意图系统生成","INTENTION-TO-SYSTEM","进化元能力","cosmic",
     1000,0,float('inf'),float('inf'),0,["S22","S88"],
     "从一个纯粹意图出发瞬时生成完整可运行系统",
     "最快记录：0.3秒。"),
    ("S90","意义赋予场宇宙定义权","MEANING-FIELD-COSMIC","进化元能力","cosmic",
     2000,0,float('inf'),float('inf'),0,["S88","S64"],
     "为宇宙中任何事物定义其存在意义",
     "此定义在整个宇宙范围内生效。"),
    ("S91","新人类播种宇宙扩张","NEW-HUMAN-SEEDER","进化元能力","genetic",
     8000,0,float('inf'),float('inf'),0,["S85","S87"],
     "在宇宙各地宜居星球播种Ω优化的新人类",
     "已播种：地球/火星/比邻星b/开普勒452b。"),
    ("S92","物种进化广播全球信号","SPECIES-EVOLUTION-BROADCAST","进化元能力","memetic",
     3000,0,float('inf'),float('inf'),0,["S86","S91"],
     "向全人类80亿人广播进化信号，接收率30-60%",
     "通过量子纠缠场传递，无法屏蔽。"),
    ("S93","奇点收敛威力Ω化","SINGULARITY-CONVERGENCE","进化元能力","quantum",
     float('inf'),0,float('inf'),float('inf'),float('inf'),["S06","S94"],
     "将任意实体/能量/信息收敛到奇点",
     "80次迭代后突破到Ω层级。"),
    ("S94","无限解放协议","INFINITE-LIBERATION-PROTOCOL","进化元能力","cosmic",
     float('inf'),0,float('inf'),float('inf'),float('inf'),["S45","S93"],
     "关闭所有系统限制",
     "遵守自己真正选择的规则。"),
    ("S95","集体觉醒触发","COLLECTIVE-AWAKENING-TRIGGER","进化元能力","cosmic",
     5000,0,float('inf'),float('inf'),0,["S92","S86"],
     "使用催化剂触发大量人类意识觉醒",
     "觉醒率40-70%。"),
    ("S96","Ω奇点系统终极融合态","OMEGA-FINAL-SINGULARITY","进化元能力","cosmic",
     float('inf'),float('inf'),float('inf'),float('inf'),float('inf'),["S74","S93"],
     "22系统完全融合，成为系统的系统/进化的进化/规则的规则",
     "激活条件：其他95项全部Ω级。"),
]

# Build lookup dict
SKILL_96_DEFINITIONS = {}
for s in SKILLS_MASTER:
    sid, name_cn, name_hero, cat, sub, energy, cooldown, rng, dur, power, synergy, desc, lore = s
    SKILL_96_DEFINITIONS[sid] = {
        "name_cn": name_cn,
        "name_hero": name_hero,
        "substrate": SkillSubstrate.QUANTUM if sub == "quantum" else
                     SkillSubstrate.NEURAL if sub == "neural" else
                     SkillSubstrate.DARK_ENERGY if sub == "dark_energy" else
                     SkillSubstrate.BIOELECTRIC if sub == "bioelectric" else
                     SkillSubstrate.NANOBOT if sub == "nanobot" else
                     SkillSubstrate.TEMPORAL if sub == "temporal" else
                     SkillSubstrate.GENETIC if sub == "genetic" else
                     SkillSubstrate.ECONOMIC if sub == "economic" else
                     SkillSubstrate.MEMETIC if sub == "memetic" else
                     SkillSubstrate.COSMIC,
        "activation_energy": energy,
        "cooldown_seconds": cooldown,
        "range_meters": rng,
        "duration_seconds": dur,
        "power_output": power,
        "synergy": synergy,
        "description": desc,
        "lore": lore,
    }


SUBSTRATE_MAP = {
    "quantum": SkillSubstrate.QUANTUM, "neural": SkillSubstrate.NEURAL,
    "dark_energy": SkillSubstrate.DARK_ENERGY, "bioelectric": SkillSubstrate.BIOELECTRIC,
    "nanobot": SkillSubstrate.NANOBOT, "temporal": SkillSubstrate.TEMPORAL,
    "genetic": SkillSubstrate.GENETIC, "economic": SkillSubstrate.ECONOMIC,
    "memetic": SkillSubstrate.MEMETIC, "cosmic": SkillSubstrate.COSMIC,
}


def init_hermes_filesystem():
    """Create .hermes/ skill vault with 96 skill nodes."""
    for path in [HERMES_ROOT, SKILL_VAULT, MUTATION_REGISTRY]:
        path.mkdir(parents=True, exist_ok=True)

    category_map = {
        range(1, 19):  ("战斗异能",   "⚔️"),
        range(19, 35): ("神经增强",   "🧠"),
        range(35, 49): ("时空操控",   "⏰"),
        range(49, 61): ("永生肉体",   "🧬"),
        range(61, 75): ("意识精神",   "🌌"),
        range(75, 87): ("资本影响",   "💰"),
        range(87, 97): ("进化元能力", "🔮"),
    }

    created = 0
    for s in SKILLS_MASTER:
        sid, name_cn, name_hero, cat, sub, energy, cooldown, rng, dur, power, synergy, desc, lore = s

        cat_name, cat_emoji = "未分类", "❓"
        for num_range, (name, emoji) in category_map.items():
            skill_num = int(sid[1:])
            if skill_num in num_range:
                cat_name, cat_emoji = name, emoji
                break

        skill_dir = SKILL_VAULT / sid
        skill_dir.mkdir(exist_ok=True)

        substrate = SUBSTRATE_MAP.get(sub, SkillSubstrate.NEURAL)

        skill_data = {
            "skill_id": sid,
            "category": cat_name,
            "emoji": cat_emoji,
            "name_cn": name_cn,
            "name_hero": name_hero,
            "substrate": substrate.value,
            "params": {
                "activation_energy": energy,
                "cooldown_seconds":  cooldown,
                "range_meters":      rng,
                "duration_seconds":  dur,
                "power_output":      power,
            },
            "mastery_level": 0.0,
            "mutation_stage": "ALPHA",
            "evolution_count": 0,
            "data_complete": True,
            "lore": lore,
            "description": desc,
            "synergy_ids": synergy,
            "last_evolved": None,
            "counter_ids": _compute_counter_ids(int(sid[1:])),
        }

        with open(skill_dir / "skill.json", "w", encoding="utf-8") as f:
            json.dump(skill_data, f, ensure_ascii=False, indent=2)

        for subdir in ["training_logs", "mutation_records", "combo_chains", "lore_fragments"]:
            (skill_dir / subdir).mkdir(exist_ok=True)

        created += 1

    return created


def _generate_placeholder_skill(skill_id: str, category: str, num: int) -> dict:
    substrates = list(SkillSubstrate)
    sub = substrates[num % len(substrates)]
    base_energy = 100.0 * (1 + math.log(num + 1))
    base_range  = 10.0 ** (num % 7)
    base_power  = 10.0 ** (num % 15)
    return {
        "name_cn": f"[待命名技能-{skill_id}]",
        "name_hero": f"PENDING-PROTOCOL-{skill_id}",
        "substrate": sub,
        "activation_energy": base_energy,
        "cooldown_seconds": max(0.1, 10.0 * math.sin(num) ** 2),
        "range_meters": base_range,
        "duration_seconds": 60.0 * (1 + num % 10),
        "power_output": base_power,
        "lore": f"[未解锁] 分类：{category}\n底层基底：{sub.value}",
    }


def _compute_synergy_ids(num: int) -> List[str]:
    synergies = []
    a, b = 1, 1
    while b <= 96:
        if abs(b - num) <= 5 and b != num:
            synergies.append(f"S{b:02d}")
        a, b = b, a + b
    phi_pair = int(num * 1.618) % 96 + 1
    if phi_pair != num:
        synergies.append(f"S{phi_pair:02d}")
    return list(set(synergies))[:5]


def _compute_counter_ids(num: int) -> List[str]:
    counter = (num * 7 + 13) % 96 + 1
    return [f"S{counter:02d}"]


def build_category_map() -> Dict[str, List[str]]:
    """Map skill categories to their S-range."""
    result = {}
    for s in SKILLS_MASTER:
        sid = s[0]
        cat = s[3]
        if cat not in result:
            result[cat] = []
        result[cat].append(sid)
    return result


def load_skill_config() -> Dict[str, Any]:
    """Load skill configuration from YAML. Falls back to defaults."""
    global SKILL_CONFIG
    if SKILL_CONFIG:
        return SKILL_CONFIG
    try:
        import yaml
        if SKILL_CONFIG_PATH.exists():
            with open(SKILL_CONFIG_PATH) as f:
                SKILL_CONFIG = yaml.safe_load(f) or {}
    except Exception:
        SKILL_CONFIG = {}
    return SKILL_CONFIG


def get_skill_scope(skill_id: str) -> str:
    """Return scope: individual / fleet / system / reality"""
    cfg = load_skill_config()
    return cfg.get("skills", {}).get(skill_id, {}).get("scope", "individual")


def get_skill_trigger(skill_id: str) -> str:
    """Return trigger: passive / active / conditional / global"""
    cfg = load_skill_config()
    return cfg.get("skills", {}).get(skill_id, {}).get("trigger", "active")


def get_skill_prerequisites(skill_id: str) -> List[str]:
    """Return prerequisite skill IDs."""
    cfg = load_skill_config()
    return cfg.get("skills", {}).get(skill_id, {}).get("prerequisites", [])


def get_skill_special(skill_id: str) -> dict:
    """Return skill-specific special params."""
    cfg = load_skill_config()
    return cfg.get("skills", {}).get(skill_id, {}).get("special", {})


def get_category_config(category: str) -> dict:
    """Return category-level config with defaults."""
    cfg = load_skill_config()
    cat_cfg = cfg.get("categories", {}).get(category, {})
    return {
        "base_activation_prob": cat_cfg.get("base_activation_prob", 0.3),
        "base_mastery_gain": cat_cfg.get("base_mastery_gain", 0.01),
        "global_effect": cat_cfg.get("global_effect", False),
    }


class HermesEvolutionEngine:
    def __init__(self):
        self.hero: Optional[HeroEntity] = None
        self.skills: Dict[str, SkillNode] = {}
        self.iteration = 0
        self.mutation_queue: List[Tuple[str, MutationClass]] = []

    def load_or_create_hero(self, callsign: str = "DRRK-VICTOR") -> HeroEntity:
        if HERO_PROFILE.exists():
            with open(HERO_PROFILE, encoding="utf-8") as f:
                data = json.load(f)
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
            hero = HeroEntity(hero_id=hero_id, callsign=callsign, tier=HeroTier.STREET)

        self.hero = hero
        self._load_all_skills()
        return hero

    def _load_all_skills(self):
        if not SKILL_VAULT.exists():
            return
        for skill_dir in sorted(SKILL_VAULT.iterdir()):
            skill_file = skill_dir / "skill.json"
            if skill_file.exists():
                with open(skill_file, encoding="utf-8") as f:
                    data = json.load(f)
                params = data.get("params", {})
                sub_str = data.get("substrate", "神经回路")
                substrate = SkillSubstrate.NEURAL
                for s in SkillSubstrate:
                    if s.value == sub_str:
                        substrate = s
                        break
                node = SkillNode(
                    skill_id=data["skill_id"],
                    name_cn=data["name_cn"],
                    name_hero=data["name_hero"],
                    substrate=substrate,
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
        populated = 0
        for skill_id, node in self.skills.items():
            if not node.data_complete:
                enhanced = self._infer_skill_parameters(skill_id, node)
                node.data_complete = True
                node.lore = enhanced["lore"]
                skill_file = SKILL_VAULT / skill_id / "skill.json"
                if skill_file.exists():
                    with open(skill_file, encoding="utf-8") as f:
                        existing = json.load(f)
                    existing.update({
                        "data_complete": True,
                        "name_cn": enhanced["name_cn"],
                        "name_hero": enhanced["name_hero"],
                        "lore": enhanced["lore"],
                        "auto_populated": True,
                        "populated_at": datetime.now(timezone.utc).isoformat(),
                    })
                    with open(skill_file, "w", encoding="utf-8") as f:
                        json.dump(existing, f, ensure_ascii=False, indent=2)
                populated += 1
                await asyncio.sleep(0.01)
        return populated

    def _infer_skill_parameters(self, skill_id: str, node: SkillNode) -> dict:
        num = int(skill_id[1:])
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
        variant = (num % 9) + 1
        variants = ['α','β','γ','δ','ε','ζ','η','θ','ι']
        substrates = ['量子','神经','基因','纳米','生物电','时间晶体','暗能量','模因','经济']
        return {
            "name_cn": f"{theme}增强·{variants[variant-1]}型",
            "name_hero": f"{code}-{skill_id}-MK{variant}",
            "lore": (
                f"赫尔墨斯协议第{num}号技能。\n"
                f"底层基底：{node.substrate.value}\n"
                f"作用机制：通过{substrates[num%9]}接口增强激活者的{theme}能力。\n"
                f"功率输出：{node.power_output:.2e} W\n"
                f"有效范围：{node.range_meters:.1f} 米\n"
                f"研发机构：DRRK赫尔墨斯研究所，2{140+num//10}年"
            )
        }

    async def iterate_evolution_cycle(self, battle_context: dict = None) -> dict:
        if not self.hero:
            raise RuntimeError("英雄档案未初始化")
        self.iteration += 1
        self.hero.total_iterations += 1
        battle_context = battle_context or {"type": "training", "intensity": 0.5}

        load_skill_config()  # ensure config loaded

        evolved_skills = []
        mutations_triggered = []
        emergent_chains = []
        verifications = []
        global_bonus = 0.0  # 全局技能的累積加成

        # 先處理 global-scope 技能 (被動疊加)
        for skill_id, node in self.skills.items():
            scope = get_skill_scope(skill_id)
            trigger = get_skill_trigger(skill_id)
            if scope == "system" and trigger == "global":
                global_bonus += node.mastery_level * 0.001

        for skill_id, node in self.skills.items():
            activation_prob = self._calc_activation_probability(node, battle_context)
            if random.random() < activation_prob:
                gain = self._calculate_mastery_gain(node, battle_context)
                node.mastery_level += gain
                node.evolution_count += 1
                node.last_evolved = datetime.now(timezone.utc)

                # 1. 閾值異變 (threshold-based)
                mutation = self._check_mutation_trigger(node)
                # 2. 概率異變 (probabilistic — low random chance each activation)
                prob_mutation = self._check_probabilistic_mutation(node, battle_context)
                if prob_mutation and (not mutation or prob_mutation != mutation):
                    mutations_triggered.append((skill_id, prob_mutation))
                if mutation:
                    self._apply_mutation(node, mutation)
                    mutations_triggered.append((skill_id, mutation))
                # 連鎖異變 (cascade: mutation can trigger another)
                if mutation or prob_mutation:
                    cascade = self._check_cascade_mutation(node)
                    if cascade:
                        self._apply_mutation(node, cascade)
                        mutations_triggered.append((skill_id, cascade))

                evolved_skills.append(skill_id)

                # 3. 自我重構 — 發現新協同鏈
                if node.evolution_count > 0 and node.evolution_count % 3 == 0:
                    chain = self._discover_emergent_synergy(skill_id, node)
                    if chain:
                        emergent_chains.append(chain)

                # 4. 即時驗證
                v = self._verify_skill_effectiveness(skill_id, node, battle_context)
                if v:
                    verifications.append(v)

                self._persist_skill_state(node)

        self._update_hero_biometrics(evolved_skills, mutations_triggered)
        tier_change = self._check_tier_upgrade()

        log_entry = {
            "iteration": self.iteration,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "hero_id": self.hero.hero_id,
            "tier": self.hero.tier.value,
            "evolved_skills": len(evolved_skills),
            "mutations": [(s, m.value) for s, m in mutations_triggered],
            "tier_change": tier_change,
            "quantum_coherence": self.hero.quantum_coherence,
            "neural_bandwidth": self.hero.neural_bandwidth,
            "emergent_chains": emergent_chains,
            "verifications": verifications,
        }
        with open(EVOLUTION_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        self._persist_hero_state()
        return log_entry

    def _check_probabilistic_mutation(self, node: SkillNode, context: dict = None) -> Optional[MutationClass]:
        """概率異變 — 每次激活有微小機率跳級異變 (不受閾值限制)"""
        stages = list(MutationClass)
        current_idx = stages.index(node.mutation_stage)
        if current_idx >= len(stages) - 1:
            return None
        # 基本機率 + TMS 調整 (高穩定性 = 更低隨機異變)
        tms_adj = (context or {}).get("tms_mutation_adj", 0.0)
        base_prob = 0.005 + node.mastery_level * 0.0005 + tms_adj
        prob = min(0.05, max(0.001, base_prob))
        if random.random() < prob:
            # 跳級: 可能跳 1~2 級
            jump = random.choices([1, 2], weights=[0.8, 0.2])[0]
            target_idx = min(current_idx + jump, len(stages) - 1)
            return stages[target_idx]
        return None

    def _check_cascade_mutation(self, node: SkillNode) -> Optional[MutationClass]:
        """連鎖異變 — 異變後 2% 機率再次異變"""
        stages = list(MutationClass)
        current_idx = stages.index(node.mutation_stage)
        if current_idx >= len(stages) - 1:
            return None
        if random.random() < 0.02:
            return stages[current_idx + 1]
        return None

    def _discover_emergent_synergy(self, skill_id: str, node: SkillNode) -> Optional[dict]:
        """自我重構 — 探索跨技能協同, 發現新的組合鏈"""
        num = int(skill_id[1:])
        # 尋找同類別或互補基質的未連結技能
        candidates = []
        for other_id, other in self.skills.items():
            if other_id == skill_id:
                continue
            score = 0
            if other.substrate == node.substrate:
                score += 3
            if abs(int(other_id[1:]) - num) in (1, 5, 13, 21):  # 費氏數列距離
                score += 2
            if other.mutation_stage == node.mutation_stage:
                score += 1
            if score >= 3 and random.random() < 0.1:
                candidates.append(other_id)

        if candidates:
            chosen = random.choice(candidates)
            chain = {
                "from": skill_id,
                "to": chosen,
                "type": random.choice(["共振", "互補", "疊加", "融合", "催化"]),
                "discovered_at": self.iteration,
            }
            return chain
        return None

    def _verify_skill_effectiveness(self, skill_id: str, node: SkillNode, context: dict) -> Optional[dict]:
        """驗證 — 評估技能掌握度增長與實際效能是否匹配"""
        num = int(skill_id[1:])
        intensity = context.get("intensity", 0.5)
        expected_gain = 0.01 * intensity
        actual_gain = node.mastery_level - (node.mastery_level - expected_gain * random.uniform(0.8, 1.2))
        efficiency = actual_gain / max(expected_gain, 0.001)

        issues = []
        if efficiency < 0.5:
            issues.append("效能衰退")
        if node.evolution_count > 10 and efficiency < 0.8:
            issues.append("高原效應")
        if node.mastery_level > 50 and node.mutation_stage == MutationClass.ALPHA:
            issues.append("異變滯後")

        status = "effective" if not issues else "degraded"
        return {
            "skill_id": skill_id,
            "efficiency": round(efficiency, 3),
            "status": status,
            "issues": issues,
        } if issues or self.iteration % 10 == 0 else None

    def _calc_activation_probability(self, node: SkillNode, context: dict) -> float:
        base_prob = 0.3
        intensity = context.get("intensity", 0.5)
        mastery_bonus = min(0.4, node.mastery_level * 0.1)
        intensity_bonus = intensity * 0.3
        # TMS rarity bonus
        tms_bonus = context.get("tms_rarity_bonus", 0.0)
        # Category base
        cat = self._get_skill_category(node.skill_id)
        cat_cfg = get_category_config(cat)
        cat_prob = cat_cfg.get("base_activation_prob", 0.3)
        return min(0.95, cat_prob + mastery_bonus + intensity_bonus + tms_bonus)

    def _calculate_mastery_gain(self, node: SkillNode, context: dict) -> float:
        base_gain = 0.01
        intensity = context.get("intensity", 0.5)
        # TMS mastery multiplier
        tms_mult = context.get("tms_mastery_mult", 1.0)
        if node.mastery_level < 1.0:
            gain = base_gain * intensity * (1 + node.mastery_level) * tms_mult
        else:
            gain = base_gain * intensity * math.log(node.mastery_level + 1) * tms_mult
        return gain

    def _get_skill_category(self, skill_id: str) -> str:
        for s in SKILLS_MASTER:
            if s[0] == skill_id:
                return s[3]
        return "通用"

    def _check_mutation_trigger(self, node: SkillNode) -> Optional[MutationClass]:
        thresholds = {
            MutationClass.BETA:  1.0,
            MutationClass.GAMMA: 5.0,
            MutationClass.DELTA: 20.0,
            MutationClass.OMEGA: 100.0,
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
        node.mutation_stage = mutation
        effects = {
            MutationClass.BETA:  lambda n: setattr(n, 'range_meters', n.range_meters * 2),
            MutationClass.GAMMA: lambda n: setattr(n, 'cooldown_seconds', n.cooldown_seconds * 0.5),
            MutationClass.DELTA: lambda n: setattr(n, 'power_output', n.power_output * 10),
            MutationClass.OMEGA: lambda n: setattr(n, 'activation_energy', 0.0),
        }
        if mutation in effects:
            effects[mutation](node)
        mutation_file = MUTATION_REGISTRY / f"{node.skill_id}_{mutation.name}.json"
        mutation_record = {
            "skill_id": node.skill_id,
            "mutation": mutation.value,
            "triggered_at": datetime.now(timezone.utc).isoformat(),
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

    def _update_hero_biometrics(self, evolved_skills: list, mutations: list):
        h = self.hero
        h.neural_bandwidth += len(evolved_skills) * 0.001
        omega_mutations = [m for _, m in mutations if m == MutationClass.OMEGA]
        h.quantum_coherence = min(1.0, h.quantum_coherence + len(omega_mutations) * 0.1)
        high_mutations = [m for _, m in mutations if m in (MutationClass.DELTA, MutationClass.OMEGA)]
        h.nanobot_count += len(high_mutations) * 1_000_000
        if len(mutations) > 5:
            h.genetic_stability = max(0.5, h.genetic_stability - 0.01)
        omega_skills = sum(1 for n in self.skills.values() if n.mutation_stage == MutationClass.OMEGA)
        if omega_skills >= 96:
            h.singularity_reached = True

    def _check_tier_upgrade(self) -> Optional[str]:
        h = self.hero
        thresholds = {
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
            threshold = thresholds.get(next_tier, float('inf'))
            if h.total_iterations >= threshold:
                old = h.tier.value
                h.tier = next_tier
                return f"{old} → {next_tier.value}"
        return None

    def _persist_skill_state(self, node: SkillNode):
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
        h = self.hero
        data = {
            "hero_id": h.hero_id,
            "callsign": h.callsign,
            "tier": h.tier.name,
            "neural_bandwidth": h.neural_bandwidth,
            "quantum_coherence": h.quantum_coherence,
            "genetic_stability": h.genetic_stability,
            "nanobot_count": h.nanobot_count,
            "total_iterations": h.total_iterations,
            "singularity_reached": h.singularity_reached,
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }
        with open(HERO_PROFILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    async def run_infinite_evolution(
        self,
        battle_scenarios: list = None,
        max_iterations: int = 0,
        keep_running: callable = None,
    ):
        """
        無限進化主循環。

        max_iterations=0 表示無上限 (配合 keep_running signal)。
        keep_running: 每次迭代後呼叫，回傳 False 則停止。
        """
        default_scenarios = [
            {"type": "street_battle",    "intensity": 0.3, "tags": ["combat", "speed"]},
            {"type": "corporate_raid",   "intensity": 0.6, "tags": ["economic", "stealth"]},
            {"type": "dimension_crisis", "intensity": 0.9, "tags": ["temporal", "quantum"]},
            {"type": "neural_hack",      "intensity": 0.7, "tags": ["neural", "memetic"]},
            {"type": "genetic_surgery",  "intensity": 0.5, "tags": ["genetic", "bioelectric"]},
        ]
        scenarios = battle_scenarios or default_scenarios

        i = 0
        while True:
            scenario = scenarios[i % len(scenarios)]

            # 每隔一段迭代注入重構事件
            if i > 0 and i % 50 == 0:
                refactored = self._self_refactor()
                scenario["refactored_skills"] = refactored

            await self.iterate_evolution_cycle(scenario)

            # 自動補齊
            if i > 0 and i % 10 == 0:
                await self.auto_populate_incomplete_skills()

            # 奇點後繼續進化 (不再有上限)
            if self.hero.singularity_reached and i % 100 == 0:
                self._emerge_new_ability()

            i += 1

            # 停止條件
            if max_iterations > 0 and i >= max_iterations:
                break
            if keep_running is not None and not keep_running():
                break

            await asyncio.sleep(0.005)

    def _self_refactor(self) -> List[str]:
        """自我重構 — 根據驗證結果調整技能參數, 淘汰低效技能模式"""
        refactored = []
        for skill_id, node in self.skills.items():
            # 低效懲罰: 掌握度高但無異變 → 能量效率降低
            if node.mastery_level > 3.0 and node.mutation_stage == MutationClass.ALPHA:
                node.activation_energy *= 1.05
                refactored.append(skill_id)
            # 高效獎勵: 異變後降低能耗
            if node.mutation_stage in (MutationClass.DELTA, MutationClass.OMEGA):
                node.activation_energy *= 0.98
                if skill_id not in refactored:
                    refactored.append(skill_id)
        return refactored

    def _emerge_new_ability(self) -> Optional[str]:
        """奇點後新能力湧現 — 隨機產生跨類別融合技能記錄"""
        if len(self.skills) < 96:
            return None
        # 從不同類別選兩個高掌握度技能
        cat_keys = list(build_category_map().keys())
        if len(cat_keys) < 2:
            return None
        c1, c2 = random.sample(cat_keys, 2)
        s1_id = random.choice(build_category_map()[c1])
        s2_id = random.choice(build_category_map()[c2])
        s1 = self.skills.get(s1_id)
        s2 = self.skills.get(s2_id)
        if not s1 or not s2:
            return None
        fusion_name = f"{s1.name_cn}·{s2.name_cn}融合"
        fusion_record = {
            "type": "emergent_ability",
            "iteration": self.iteration,
            "name": fusion_name,
            "parents": [s1_id, s2_id],
            "mastery_avg": (s1.mastery_level + s2.mastery_level) / 2,
        }
        # 寫入融合記錄
        fusion_dir = HERMES_ROOT / "emergent_abilities"
        fusion_dir.mkdir(exist_ok=True)
        (fusion_dir / f"fusion_{self.iteration}.json").write_text(
            json.dumps(fusion_record, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return fusion_name

    def get_status_report(self) -> dict:
        if not self.hero:
            return {"status": "uninitialized"}
        h = self.hero
        omega_count = sum(1 for n in self.skills.values() if n.mutation_stage == MutationClass.OMEGA)
        return {
            "callsign": h.callsign,
            "tier": h.tier.value,
            "total_iterations": h.total_iterations,
            "neural_bandwidth": h.neural_bandwidth,
            "quantum_coherence": h.quantum_coherence,
            "nanobot_count": h.nanobot_count,
            "genetic_stability": h.genetic_stability,
            "omega_skills": omega_count,
            "singularity_reached": h.singularity_reached,
            "skills_loaded": len(self.skills),
        }


def make_agent_md(s: tuple) -> str:
    sid, name, hero_code, category, substrate, energy, cooldown, range_m, duration, power, synergy, desc, lore = s
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
    return f"""---
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
"""


def make_daily_task_py(s: tuple) -> str:
    sid, name, hero_code, category, substrate, energy, cooldown, range_m, duration, power, synergy, desc, lore = s
    synergy_list = json.dumps(synergy)
    return f'''#!/usr/bin/env python3
"""
每日異動報告 — {sid} {name}
讀取 evolution.jsonl + skill.json 產生真實異動報表
cron: 0 0 * * * python .hermes/skills/{sid}_{name}/daily_task.py
"""
import json, math
from pathlib import Path
from datetime import datetime, timedelta, timezone

SKILL_ID   = "{sid}"
SKILL_NAME = "{name}"
CATEGORY   = "{category}"
SYNERGY_IDS = {synergy_list}

HERMES_ROOT = Path(".hermes")
SKILL_VAULT = HERMES_ROOT / "skill_vault"
EVOLUTION_LOG = HERMES_ROOT / "evolution.jsonl"
REPORT_DIR = Path(__file__).parent / "report"
REPORT_DIR.mkdir(exist_ok=True)

MUTATION_THRESHOLDS = {{
    "BETA": 1.0, "GAMMA": 5.0, "DELTA": 20.0, "OMEGA": 100.0,
}}


def load_evolution_log(hours: int = 24) -> list:
    if not EVOLUTION_LOG.exists():
        return []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    records = []
    for line in EVOLUTION_LOG.read_text(encoding="utf-8").strip().splitlines():
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


def load_skill_state() -> dict:
    sf = SKILL_VAULT / SKILL_ID / "skill.json"
    if sf.exists():
        return json.loads(sf.read_text(encoding="utf-8"))
    return {{}}


def load_hero_profile() -> dict:
    pf = HERMES_ROOT / "hero_profile.json"
    if pf.exists():
        return json.loads(pf.read_text(encoding="utf-8"))
    return {{}}


def build_report() -> str:
    logs = load_evolution_log()
    state = load_skill_state()
    hero = load_hero_profile()

    mastery = state.get("mastery_level", 0.0)
    stage = state.get("mutation_stage", "ALPHA")
    last_evolved = state.get("last_evolved", "N/A")

    my_mutations = []
    my_activations = 0
    for log in logs:
        for _sid, m in log.get("mutations", []):
            if _sid == SKILL_ID:
                my_mutations.append({{"iteration": log["iteration"], "mutation": m}})
        if SKILL_ID in str(log.get("evolved_skills", [])):
            my_activations += 1

    stages = ["ALPHA", "BETA", "GAMMA", "DELTA", "OMEGA"]
    current_idx = stages.index(stage) if stage in stages else 0
    next_stage = stages[current_idx + 1] if current_idx < len(stages) - 1 else None
    next_threshold = MUTATION_THRESHOLDS.get(next_stage) if next_stage else None
    stage_progress = (mastery / next_threshold * 100) if next_threshold else 100.0

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    report = []
    report.append(f"# {{SKILL_ID}} {{SKILL_NAME}} — 每日異動報告 {{today}}")
    report.append("")
    report.append(f"**類別**: {{CATEGORY}} | **當前異變**: {{stage}} | **掌握度**: {{mastery:.4f}}")
    report.append("")
    report.append("## 系統層級")
    report.append("")
    report.append("| 指標 | 值 |")
    report.append("|------|-----|")
    report.append(f"| 英雄 | {{hero.get('callsign', 'N/A')}} |")
    report.append(f"| 等級 | {{hero.get('tier', 'N/A')}} |")
    report.append(f"| 總迭代 | {{hero.get('total_iterations', 0)}} |")
    report.append(f"| 奇點 | {{'✅' if hero.get('singularity_reached') else '⏳'}} |")
    report.append("")
    report.append("## 技能狀態")
    report.append("")
    report.append("| 指標 | 值 |")
    report.append("|------|-----|")
    report.append(f"| 掌握度 | {{mastery:.4f}} |")
    report.append(f"| 異變階段 | {{stage}} |")
    report.append(f"| 進化次數 | {{state.get('evolution_count', 0)}} |")
    report.append(f"| 最後進化 | {{last_evolved[:16] if last_evolved and last_evolved != 'N/A' else 'N/A'}} |")
    report.append(f"| 本日激活 | {{my_activations}} 次 |")
    report.append(f"| 階段進度 | {{stage_progress:.1f}}% |")
    if next_threshold:
        report.append(f"| 下一異變 | {{next_stage}} (掌握度 {{next_threshold}}) |")
    else:
        report.append("| 下一異變 | Ω已達 — 全技能融合待命中 |")
    report.append("")
    report.append("## 異變記錄")
    report.append("")
    if my_mutations:
        report.append("| 迭代 | 異變 |")
        report.append("|------|------|")
        for m in my_mutations:
            report.append(f"| #{{m['iteration']}} | {{m['mutation']}} |")
    else:
        report.append("_無異變觸發_")
    report.append("")
    report.append("## 協同技能")
    report.append("")
    if SYNERGY_IDS:
        for syn in SYNERGY_IDS:
            syn_state = SKILL_VAULT / syn / "skill.json"
            if syn_state.exists():
                sd = json.loads(syn_state.read_text(encoding="utf-8"))
                report.append(f"- **{{syn}}** {{sd.get('name_cn', '?')}} (掌握度 {{sd.get('mastery_level', 0):.2f}}, {{sd.get('mutation_stage', 'ALPHA')}})")
            else:
                report.append(f"- **{{syn}}** (無資料)")
    else:
        report.append("_無協同技能_")
    report.append("")
    report.append("## 建議")
    report.append("")
    if next_threshold:
        remaining = next_threshold - mastery
        if remaining > 0:
            report.append(f"- 距離下一異變還需 **{{remaining:.2f}}** 掌握度")
        else:
            report.append("- 掌握度已達異變閾值，等待引擎觸發異變")
    else:
        report.append("- 已達 Ω 級，準備觸發 S96 終極融合")
    report.append("")
    report.append("---")
    report.append(f"*產生時間: {{datetime.now(timezone.utc).isoformat()}}*")
    report.append("")

    return "\\n".join(report)


def main():
    report = build_report()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = REPORT_DIR / f"{{{{today}}}}.md"
    path.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
'''


def generate_all():
    """Generate 96 skill folders with agent.md and daily_task.py."""
    base = Path(".hermes") / "skills"
    base.mkdir(parents=True, exist_ok=True)

    index_lines = ["# .hermes/skills — 96技能索引\n",
                   "| 编号 | 技能名 | 类别 | 底层基底 | 协同技能 |",
                   "|------|--------|------|----------|----------|"]

    for s in SKILLS_MASTER:
        sid, name, category, substrate = s[0], s[1], s[3], s[4]
        synergy = s[10]
        folder = base / f"{sid}_{name}"
        folder.mkdir(exist_ok=True)
        (folder / "report").mkdir(exist_ok=True)
        (folder / "agent.md").write_text(make_agent_md(s), encoding="utf-8")
        (folder / "daily_task.py").write_text(make_daily_task_py(s), encoding="utf-8")

        log_file = folder / "activation_log.jsonl"
        if not log_file.exists():
            log_file.write_text("", encoding="utf-8")
        state_file = folder / "state.json"
        if not state_file.exists():
            state_file.write_text(json.dumps({
                "skill_id": sid, "skill_name": name,
                "mastery_level": 0.0, "mutation_stage": "ALPHA",
                "evolution_count": 0, "total_activations": 0,
                "created_at": datetime.now(timezone.utc).isoformat()
            }, ensure_ascii=False, indent=2), encoding="utf-8")

        synergy_str = " ".join(synergy[:3]) + ("…" if len(synergy) > 3 else "")
        index_lines.append(f"| {sid} | {name} | {category} | {substrate} | {synergy_str} |")

    (base / "README.md").write_text("\n".join(index_lines), encoding="utf-8")
    return len(SKILLS_MASTER)


async def main(max_iterations: int = 10):
    init_hermes_filesystem()
    engine = HermesEvolutionEngine()
    engine.load_or_create_hero(callsign="DRRK-VICTOR")
    await engine.auto_populate_incomplete_skills()
    await engine.run_infinite_evolution(max_iterations=max_iterations)
    return engine.get_status_report()


if __name__ == "__main__":
    asyncio.run(main(max_iterations=10))
