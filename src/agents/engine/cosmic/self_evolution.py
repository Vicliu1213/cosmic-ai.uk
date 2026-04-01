#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自进化学习系统 - 用于 Cosmic Engine
Self-Evolution Learning System for Cosmic Engine

实现：
- PPO (近端策略优化) 强化学习
- CMA-ES 进化策略
- 知识蒸馏
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from collections import defaultdict, deque
import json

logger = logging.getLogger(__name__)


class LearningPhase(Enum):
    """学习阶段"""
    EXPLORATION = "exploration"     # 探索
    EXPLOITATION = "exploitation"   # 利用
    ADAPTATION = "adaptation"       # 适应


@dataclass
class Experience:
    """经验数据"""
    state: np.ndarray
    action: int
    reward: float
    next_state: np.ndarray
    done: bool
    timestamp: float


@dataclass
class PolicyUpdate:
    """策略更新记录"""
    episode: int
    loss: float
    policy_gradient: np.ndarray
    improvement: float
    timestamp: str


class PPOLearner:
    """PPO (近端策略优化) 学习器"""
    
    def __init__(
        self,
        state_dim: int = 128,
        action_dim: int = 32,
        learning_rate: float = 3e-4,
        gamma: float = 0.99,
        clip_ratio: float = 0.2
    ):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.clip_ratio = clip_ratio
        
        # 策略参数
        self.policy_weights = np.random.randn(state_dim, action_dim) * 0.01
        self.value_weights = np.random.randn(state_dim, 1) * 0.01
        
        # 优化状态
        self.experience_buffer: deque = deque(maxlen=100000)
        self.policy_updates: List[PolicyUpdate] = []
        self.total_episodes = 0
    
    def get_action(self, state: np.ndarray) -> Tuple[int, float]:
        """获取动作和对数概率"""
        logits = state @ self.policy_weights  # shape: (action_dim,)
        action_probs = self._softmax(logits)
        
        action = np.random.choice(self.action_dim, p=action_probs)
        log_prob = np.log(action_probs[action] + 1e-10)
        
        return action, log_prob
    
    def compute_advantages(
        self,
        states: List[np.ndarray],
        rewards: List[float],
        next_states: List[np.ndarray],
        dones: List[bool]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """计算优势函数"""
        
        values = np.array([state @ self.value_weights for state in states]).squeeze()
        next_values = np.array([state @ self.value_weights for state in next_states]).squeeze()
        
        # TD 目标
        td_targets = []
        for i, (reward, done) in enumerate(zip(rewards, dones)):
            if done:
                td_target = reward
            else:
                td_target = reward + self.gamma * next_values[i]
            td_targets.append(td_target)
        
        td_targets = np.array(td_targets)
        advantages = td_targets - values
        
        # 标准化优势
        advantages = (advantages - np.mean(advantages)) / (np.std(advantages) + 1e-10)
        
        return advantages, np.array(td_targets)
    
    def update_policy(
        self,
        states: List[np.ndarray],
        actions: List[int],
        old_log_probs: List[float],
        advantages: np.ndarray,
        td_targets: np.ndarray,
        epochs: int = 3
    ) -> float:
        """更新策略"""
        
        total_loss = 0.0
        
        for epoch in range(epochs):
            # 小批量更新
            batch_size = min(32, len(states))
            indices = np.random.choice(len(states), batch_size, replace=False)
            
            for idx in indices:
                state = states[idx]
                action = actions[idx]
                old_log_prob = old_log_probs[idx]
                advantage = advantages[idx]
                td_target = td_targets[idx]
                
                # 前向传播
                logits = state @ self.policy_weights
                action_probs = self._softmax(logits)
                new_log_prob = np.log(action_probs[action] + 1e-10)
                
                # 策略损失 (PPO clipped objective)
                ratio = np.exp(new_log_prob - old_log_prob)
                surr1 = ratio * advantage
                surr2 = np.clip(ratio, 1 - self.clip_ratio, 1 + self.clip_ratio) * advantage
                policy_loss = -np.minimum(surr1, surr2)
                
                # 价值损失
                value_pred = state @ self.value_weights
                value_loss = (value_pred - td_target) ** 2
                
                # 总损失
                loss = policy_loss + 0.5 * value_loss
                total_loss += loss
                
                # 梯度更新 (简化版)
                grad_scale = self.learning_rate * loss
                self.policy_weights -= grad_scale * state[:, np.newaxis] @ np.ones((1, self.action_dim))
                self.value_weights -= self.learning_rate * (value_pred - td_target) * state[:, np.newaxis]
        
        avg_loss = total_loss / (epochs * batch_size)
        self.total_episodes += 1
        
        return avg_loss
    
    def _softmax(self, x: np.ndarray) -> np.ndarray:
        """Softmax 函数"""
        e_x = np.exp(x - np.max(x))
        return e_x / e_x.sum()
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """获取学习统计"""
        return {
            'total_episodes': self.total_episodes,
            'experience_buffer_size': len(self.experience_buffer),
            'policy_updates': len(self.policy_updates),
            'learning_rate': self.learning_rate,
            'gamma': self.gamma
        }


class CMAESEvolutionStrategy:
    """CMA-ES 进化策略"""
    
    def __init__(
        self,
        dimensions: int = 20,
        population_size: int = 30,
        sigma_init: float = 1.0
    ):
        self.dimensions = dimensions
        self.population_size = population_size
        
        # 初始分布参数
        self.mean = np.zeros(dimensions)
        self.sigma = sigma_init
        self.C = np.eye(dimensions)              # 协方差矩阵
        self.B = np.eye(dimensions)              # 特征向量
        self.D = np.ones(dimensions)             # 特征值的平方根
        
        # 进化路径
        self.pc = np.zeros(dimensions)
        self.ps = np.zeros(dimensions)
        
        # 超参数
        self.mu = population_size // 2
        self.weights = np.log(self.mu + 0.5) - np.log(np.arange(1, self.mu + 1))
        self.weights /= self.weights.sum()
        self.mueff = 1.0 / np.sum(self.weights ** 2)
        
        # 适应系数
        self.cc = (4 + self.mueff / dimensions) / (dimensions + 4 + 2 * self.mueff / dimensions)
        self.cs = (self.mueff + 2) / (dimensions + self.mueff + 5)
        self.c1 = 2 / ((dimensions + 1.3) ** 2 + self.mueff)
        self.cmu = min(1 - self.c1, 2 * (self.mueff - 2 + 1 / self.mueff) / ((dimensions + 2) ** 2 + self.mueff))
        self.damps = 1 + 2 * max(0, np.sqrt((self.mueff - 1) / (dimensions + 1)) - 1) + self.cs
        
        # 进化历史
        self.generation = 0
        self.fitness_history = []
        self.mean_history = []
    
    def sample_population(self) -> List[np.ndarray]:
        """采样种群"""
        samples = []
        for _ in range(self.population_size):
            z = np.random.standard_normal(self.dimensions)
            y = self.B @ (self.D * z)
            x = self.mean + self.sigma * y
            samples.append(x)
        return samples
    
    def update(self, solutions: List[np.ndarray], fitness_values: List[float]):
        """更新分布"""
        
        # 排序并选择最优的 mu 个解
        sorted_idx = np.argsort(fitness_values)[:self.mu]
        selected_solutions = [solutions[i] for i in sorted_idx]
        
        # 保存历史
        self.fitness_history.append(np.mean([fitness_values[i] for i in sorted_idx]))
        
        # 更新均值
        old_mean = self.mean.copy()
        self.mean = np.sum([self.weights[i] * selected_solutions[i] 
                           for i in range(self.mu)], axis=0)
        
        # 计算进化路径用的缩放因子
        z_mean = (self.mean - old_mean) / self.sigma
        
        # 更新共轭进化路径
        self.ps = (1 - self.cs) * self.ps + np.sqrt(self.cs * (2 - self.cs)) * (self.B @ np.linalg.inv(self.D) @ self.B.T @ z_mean)
        
        # 更新进化路径
        hsig = (np.linalg.norm(self.ps) / 
               np.sqrt(1 - (1 - self.cs) ** (2 * self.generation)) / 
               np.sqrt(2 / np.pi) < 1.4 + 2 / (self.dimensions + 1))
        
        self.pc = (1 - self.cc) * self.pc + hsig * np.sqrt(self.cc * (2 - self.cc)) * z_mean
        
        # 更新协方差矩阵
        artmp = np.sqrt(self.mueff) * (self.mean - old_mean) / self.sigma
        self.C = ((1 - self.c1 - self.cmu) * self.C + 
                 self.c1 * (np.outer(self.pc, self.pc) + (1 - hsig) * self.cc * (2 - self.cc) * self.C) +
                 self.cmu * np.sum([self.weights[i] * np.outer(artmp, artmp) 
                                   for i in range(self.mu)], axis=0))
        
        # 更新步长
        self.sigma *= np.exp((self.cs / self.damps) * (np.linalg.norm(self.ps) / 
                                                       np.sqrt(1 - (1 - self.cs) ** (2 * (self.generation + 1))) - 1))
        
        # 特征分解
        eigenvalues, eigenvectors = np.linalg.eigh(self.C)
        idx = np.argsort(eigenvalues)[::-1]
        self.D = np.sqrt(eigenvalues[idx])
        self.B = eigenvectors[:, idx]
        
        self.generation += 1
        self.mean_history.append(self.mean.copy())
    
    def get_evolution_stats(self) -> Dict[str, Any]:
        """获取进化统计"""
        return {
            'generation': self.generation,
            'current_mean': self.mean.tolist(),
            'current_sigma': self.sigma,
            'fitness_history': self.fitness_history[-20:],
            'population_size': self.population_size,
            'dimensions': self.dimensions
        }


class KnowledgeDistiller:
    """知识蒸馏器"""
    
    def __init__(self, temperature: float = 3.0):
        self.temperature = temperature
        self.distillation_history = []
    
    def distill_knowledge(
        self,
        teacher_outputs: Dict[str, Any],
        student_model: Dict[str, Any]
    ) -> float:
        """蒸馏知识"""
        
        # 计算软目标 (教师输出)
        teacher_logits = teacher_outputs.get('logits', np.zeros(10))
        teacher_probs = self._softmax(teacher_logits / self.temperature)
        
        # 学生预测
        student_logits = student_model.get('logits', np.zeros(10))
        student_probs = self._softmax(student_logits / self.temperature)
        
        # KL 散度
        kl_divergence = np.sum(teacher_probs * (np.log(teacher_probs + 1e-10) - np.log(student_probs + 1e-10)))
        
        # 调整损失
        loss = kl_divergence * (self.temperature ** 2)
        
        self.distillation_history.append({
            'timestamp': datetime.now().isoformat(),
            'kl_divergence': float(kl_divergence),
            'loss': float(loss)
        })
        
        return loss
    
    def _softmax(self, x: np.ndarray) -> np.ndarray:
        """Softmax 函数"""
        e_x = np.exp(x - np.max(x))
        return e_x / e_x.sum()
    
    def get_distillation_stats(self) -> Dict[str, Any]:
        """获取蒸馏统计"""
        return {
            'total_distillations': len(self.distillation_history),
            'temperature': self.temperature,
            'recent_distillations': self.distillation_history[-10:]
        }


class SelfEvolutionEngine:
    """自进化引擎 - 整合 PPO + CMA-ES + 知识蒸馏"""
    
    def __init__(
        self,
        state_dim: int = 128,
        action_dim: int = 32,
        evolution_dims: int = 20
    ):
        self.ppo_learner = PPOLearner(state_dim, action_dim)
        self.evolution_strategy = CMAESEvolutionStrategy(evolution_dims)
        self.knowledge_distiller = KnowledgeDistiller()
        
        self.learning_phase = LearningPhase.EXPLORATION
        self.phase_transitions: List[Tuple[float, str]] = []
    
    def learn_from_experience(
        self,
        states: List[np.ndarray],
        actions: List[int],
        rewards: List[float],
        next_states: List[np.ndarray],
        dones: List[bool]
    ) -> float:
        """从经验中学习"""
        
        # 计算优势
        advantages, td_targets = self.ppo_learner.compute_advantages(
            states, rewards, next_states, dones
        )
        
        # 计算旧对数概率
        old_log_probs = [self.ppo_learner.get_action(s)[1] for s in states]
        
        # 更新策略
        loss = self.ppo_learner.update_policy(
            states, actions, old_log_probs, advantages, td_targets
        )
        
        # 根据损失调整学习阶段
        self._adjust_learning_phase(loss)
        
        return loss
    
    def evolve_strategy(
        self,
        fitness_func: Callable,
        num_generations: int = 10
    ) -> List[float]:
        """进化策略"""
        
        best_fitness = []
        
        for _ in range(num_generations):
            # 采样种群
            population = self.evolution_strategy.sample_population()
            
            # 评估
            fitness_values = [fitness_func(p) for p in population]
            
            # 更新
            self.evolution_strategy.update(population, fitness_values)
            
            best_fitness.append(np.max(fitness_values))
        
        return best_fitness
    
    def _adjust_learning_phase(self, loss: float):
        """调整学习阶段"""
        
        if loss < 0.1:
            new_phase = LearningPhase.EXPLOITATION
        elif loss < 0.5:
            new_phase = LearningPhase.ADAPTATION
        else:
            new_phase = LearningPhase.EXPLORATION
        
        if new_phase != self.learning_phase:
            self.learning_phase = new_phase
            self.phase_transitions.append((datetime.now().timestamp(), new_phase.value))
            logger.info(f"🔄 学习阶段转换 -> {new_phase.value}")
    
    def get_evolution_status(self) -> Dict[str, Any]:
        """获取进化状态"""
        return {
            'ppo_stats': self.ppo_learner.get_learning_stats(),
            'evolution_stats': self.evolution_strategy.get_evolution_stats(),
            'distillation_stats': self.knowledge_distiller.get_distillation_stats(),
            'learning_phase': self.learning_phase.value,
            'phase_transitions': self.phase_transitions[-10:]
        }


# 导出主类
__all__ = [
    'SelfEvolutionEngine',
    'PPOLearner',
    'CMAESEvolutionStrategy',
    'KnowledgeDistiller',
    'LearningPhase',
    'Experience',
    'PolicyUpdate'
]
