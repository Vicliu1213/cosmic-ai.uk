#!/usr/bin/env python3
"""
KTZEN Environment Setup Test
Development environment verification for ML/RL/Quantum projects
"""

import sys
import os

def test_environment():
    """Test all installed packages and capabilities"""
    
    print("🧪 KTZEN Environment Test")
    print("=" * 50)
    
    # Test basic packages
    print("📦 Testing Core Packages...")
    
    try:
        import numpy as np
        print(f"✅ NumPy: {np.__version__}")
    except ImportError:
        print("❌ NumPy: Not installed")
    
    try:
        import torch
        print(f"✅ PyTorch: {torch.__version__}")
        print(f"   CUDA Available: {torch.cuda.is_available()}")
    except ImportError:
        print("❌ PyTorch: Not installed")
    
    try:
        import scipy
        print(f"✅ SciPy: {scipy.__version__}")
    except ImportError:
        print("❌ SciPy: Not installed")
    
    try:
        import matplotlib.pyplot as plt
        print(f"✅ Matplotlib: {plt.matplotlib.__version__}")
    except ImportError:
        print("❌ Matplotlib: Not installed")
    
    try:
        import networkx as nx
        print(f"✅ NetworkX: {nx.__version__}")
    except ImportError:
        print("❌ NetworkX: Not installed")
    
    try:
        import qiskit
        print(f"✅ Qiskit: {qiskit.__version__}")
    except ImportError:
        print("❌ Qiskit: Not installed")
    
    try:
        import gymnasium as gym
        print(f"✅ Gymnasium: {gym.__version__}")
    except ImportError:
        print("❌ Gymnasium: Not installed")
    
    print("\n🤖 Testing ML/RL Capabilities...")
    
    # Test simple tensor operations
    try:
        import torch
        x = torch.randn(3, 4)
        y = torch.matmul(x, x.T)
        print("✅ PyTorch tensor operations working")
    except Exception as e:
        print(f"❌ PyTorch operations failed: {e}")
    
    # Test RL environment
    try:
        import gymnasium as gym
        env = gym.make('CartPole-v1')
        obs, info = env.reset()
        print(f"✅ RL Environment (CartPole): obs shape {obs.shape}")
        env.close()
    except Exception as e:
        print(f"❌ RL Environment failed: {e}")
    
    # Test quantum circuit
    try:
        from qiskit import QuantumCircuit
        qc = QuantumCircuit(2)
        qc.h(0)
        qc.cx(0, 1)
        qc.measure_all()
        print("✅ Quantum circuit creation working")
    except Exception as e:
        print(f"❌ Quantum operations failed: {e}")
    
    # Test visualization
    try:
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend
        import matplotlib.pyplot as plt
        plt.figure(figsize=(1, 1))
        plt.plot([0, 1], [0, 1])
        plt.close()
        print("✅ Visualization backend working")
    except Exception as e:
        print(f"❌ Visualization failed: {e}")
    
    print("\n📁 Environment Info:")
    print(f"Python: {sys.version}")
    print(f"Working Directory: {os.getcwd()}")
    
    # Memory info
    try:
        import psutil
        memory = psutil.virtual_memory()
        print(f"Available Memory: {memory.available / 1024**3:.1f} GB")
    except ImportError:
        print("Memory info unavailable (psutil not installed)")
    
    print("\n🎯 KTZEN Setup Complete!")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    test_environment()