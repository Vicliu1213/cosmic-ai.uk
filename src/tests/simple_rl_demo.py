#!/usr/bin/env python3
"""
Simple RL Demo using Gymnasium
Demonstrates basic reinforcement learning setup
"""

import gymnasium as gym
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import matplotlib.pyplot as plt
from collections import deque
import random

class SimpleAgent(nn.Module):
    """Simple neural network for CartPole"""
    
    def __init__(self, input_size=4, hidden_size=64, output_size=2):
        super(SimpleAgent, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, output_size)
        )
    
    def forward(self, x):
        return self.network(x)

class RLTrainer:
    """Basic RL training loop"""
    
    def __init__(self, env_name='CartPole-v1'):
        self.env = gym.make(env_name)
        self.agent = SimpleAgent()
        self.optimizer = optim.Adam(self.agent.parameters(), lr=0.001)
        self.memory = deque(maxlen=10000)
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        
        print(f"🎮 Environment: {env_name}")
        print(f"📊 State Space: {self.env.observation_space}")
        print(f"🎯 Action Space: {self.env.action_space}")
    
    def select_action(self, state):
        """Epsilon-greedy action selection"""
        if random.random() <= self.epsilon:
            return self.env.action_space.sample()
        
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state)
            q_values = self.agent(state_tensor)
            return q_values.argmax().item()
    
    def train_episode(self):
        """Train one episode"""
        state, info = self.env.reset()
        total_reward = 0
        done = False
        
        while not done:
            action = self.select_action(state)
            next_state, reward, terminated, truncated, info = self.env.step(action)
            done = terminated or truncated
            
            # Store experience
            self.memory.append((state, action, reward, next_state, done))
            
            state = next_state
            total_reward += reward
        
        # Simple training step (would be more sophisticated in real RL)
        if len(self.memory) > 32:
            self.train_step()
        
        # Decay epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        
        return total_reward
    
    def train_step(self):
        """Simple Q-learning update"""
        if len(self.memory) < 32:
            return
        
        # Sample batch
        batch = random.sample(self.memory, 32)
        states, actions, rewards, next_states, dones = zip(*batch)
        
        states = torch.FloatTensor(states)
        actions = torch.LongTensor(actions)
        rewards = torch.FloatTensor(rewards)
        next_states = torch.FloatTensor(next_states)
        dones = torch.BoolTensor(dones)
        
        # Q-values
        current_q = self.agent(states).gather(1, actions.unsqueeze(1)).squeeze()
        next_q = self.agent(next_states).max(1)[0]
        target_q = rewards + (0.99 * next_q * ~dones)
        
        # Loss
        loss = nn.MSELoss()(current_q, target_q)
        
        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
    
    def train(self, episodes=100):
        """Train for multiple episodes"""
        rewards = []
        
        print(f"\n🚀 Starting training for {episodes} episodes...")
        print("=" * 50)
        
        for episode in range(episodes):
            reward = self.train_episode()
            rewards.append(reward)
            
            if episode % 10 == 0:
                avg_reward = np.mean(rewards[-10:])
                print(f"Episode {episode:3d} | Reward: {reward:6.1f} | Avg: {avg_reward:6.1f} | Epsilon: {self.epsilon:.3f}")
        
        print("=" * 50)
        print(f"🎉 Training completed!")
        print(f"📈 Final average reward (last 10): {np.mean(rewards[-10:]):.1f}")
        
        return rewards
    
    def test(self, episodes=5):
        """Test trained agent"""
        print(f"\n🧪 Testing agent for {episodes} episodes...")
        print("=" * 30)
        
        total_rewards = []
        
        for episode in range(episodes):
            state, info = self.env.reset()
            total_reward = 0
            done = False
            step = 0
            
            while not done:
                # Greedy action (no epsilon)
                with torch.no_grad():
                    state_tensor = torch.FloatTensor(state)
                    q_values = self.agent(state_tensor)
                    action = q_values.argmax().item()
                
                state, reward, terminated, truncated, info = self.env.step(action)
                done = terminated or truncated
                total_reward += reward
                step += 1
            
            total_rewards.append(total_reward)
            print(f"Test Episode {episode+1}: Reward = {total_reward:.1f} (Steps: {step})")
        
        avg_test_reward = np.mean(total_rewards)
        print(f"📊 Average test reward: {avg_test_reward:.1f}")
        
        return total_rewards

def main():
    """Main demo function"""
    print("🤖 Simple RL Demo")
    print("Using KTZEN environment")
    print("=" * 40)
    
    # Create trainer
    trainer = RLTrainer()
    
    # Train
    rewards = trainer.train(episodes=50)
    
    # Test
    test_rewards = trainer.test(episodes=3)
    
    # Simple visualization
    try:
        plt.figure(figsize=(10, 4))
        plt.plot(rewards, label='Training Rewards', alpha=0.7)
        plt.axhline(y=195, color='r', linestyle='--', label='CartPole Success Threshold')
        plt.xlabel('Episode')
        plt.ylabel('Reward')
        plt.title('Training Progress')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Save plot
        plt.savefig('/root/comic_ai/training_plot.png')
        print("\n📈 Training plot saved to 'training_plot.png'")
        
        plt.close()
    except Exception as e:
        print(f"Visualization failed: {e}")
    
    trainer.env.close()
    print("\n✅ Demo completed successfully!")

if __name__ == "__main__":
    main()