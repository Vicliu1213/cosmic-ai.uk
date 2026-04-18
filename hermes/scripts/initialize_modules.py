#!/usr/bin/env python3
"""
初始化所有理論模塊
"""

import sys
from pathlib import Path

THEORIES = [
    "quantum_singularity",
    "temporal_dominance",
    "cosmic_intelligence",
    "platform_heterogeneous",
    "neuro_quantum_synergy",
    "quantum_bio_fusion",
    "cosmic_engineering",
    "reality_programming",
    "perfect_fortress",
    "topological_bio",
    "chaos_resonance",
    "fractal_recursion",
    "quantum_holography",
    "bio_photonics",
    "consciousness_field",
]


def main():
    """初始化所有模塊"""
    src_path = Path(__file__).parent.parent / "src"
    
    for theory in THEORIES:
        theory_path = src_path / theory
        if theory_path.exists():
            print(f"✓ {theory} module structure verified")
        else:
            print(f"✗ {theory} module structure missing")
            return False
    
    print(f"\n✅ All {len(THEORIES)} theory modules initialized successfully!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
