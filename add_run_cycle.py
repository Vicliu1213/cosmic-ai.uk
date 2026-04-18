#!/usr/bin/env python3
"""
Add run_cycle() method to all theory actors
"""

import os
from pathlib import Path

RUN_CYCLE_METHOD = '''
    def run_cycle(self, input_data=None):
        """
        標準循環處理方法
        
        Args:
            input_data: 輸入數據
            
        Returns:
            處理結果字典
        """
        import numpy as np
        
        try:
            if input_data is None:
                # 生成示例數據
                input_data = np.random.rand(10)
            
            # 將 numpy array 轉換為可序列化的格式
            if isinstance(input_data, np.ndarray):
                input_data = input_data.tolist()
            
            # 調用 process 方法
            result = self.process(input_data)
            
            return {
                "status": "success",
                "result": result,
                "is_active": self.is_active
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "is_active": self.is_active
            }
'''

def main():
    """Add run_cycle to all actor files"""
    src_path = Path(__file__).parent / "src"
    
    theories = [
        "bio_photonics",
        "chaos_resonance",
        "consciousness_field",
        "cosmic_engineering",
        "cosmic_intelligence",
        "fractal_recursion",
        "neuro_quantum_synergy",
        "perfect_fortress",
        "platform_heterogeneous",
        "quantum_bio_fusion",
        "quantum_holography",
        "reality_programming",
        "temporal_dominance",
        "topological_bio",
    ]
    
    for theory in theories:
        core_path = src_path / theory / "core.py"
        
        if not core_path.exists():
            print(f"✗ {theory}: core.py not found")
            continue
        
        # Read the file
        with open(core_path, 'r') as f:
            content = f.read()
        
        # Check if run_cycle already exists
        if "def run_cycle" in content:
            print(f"⊘ {theory}: run_cycle already exists")
            continue
        
        # Find the shutdown method and insert run_cycle before it
        if "def shutdown" in content:
            # Insert before shutdown
            content = content.replace(
                "    def shutdown",
                RUN_CYCLE_METHOD + "\n    def shutdown"
            )
        else:
            # Append at the end (before the last closing block if any)
            lines = content.rstrip().split('\n')
            # Find the last non-empty line that's not just whitespace
            last_method_idx = len(lines) - 1
            content = content.rstrip() + RUN_CYCLE_METHOD
        
        # Write back
        with open(core_path, 'w') as f:
            f.write(content)
        
        print(f"✓ {theory}: run_cycle added")
    
    print("\n✓ All run_cycle methods added successfully")

if __name__ == "__main__":
    main()
