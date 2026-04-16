#!/usr/bin/env python3
"""
遞歸超指數協同係數驗證腳本
Recursive Superexponential Synergy Coefficient Verification Script

驗證 ES 系統的 18 層遞歸乘法鏈，計算實測乘數與預期值的差異。
"""

import json
import math
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

def load_es_system_state(project_root: Path = Path("/workspaces/cosmic-ai.uk")) -> Dict:
    """加載 ES 系統狀態"""
    state_file = project_root / "exponential_synergy_network" / "system_state_export.json"
    with open(state_file) as f:
        return json.load(f)

def analyze_layers(state: Dict) -> Dict:
    """分析所有層級配置"""
    layers_data = state['layers']
    
    # 按類型分類
    layers_by_type = {}
    for layer_id, layer_info in layers_data.items():
        layer_type = layer_info['layer_type'].replace('LayerType.', '')
        if layer_type not in layers_by_type:
            layers_by_type[layer_type] = []
        layers_by_type[layer_type].append(layer_info)
    
    # 排序
    for layer_type in layers_by_type:
        layers_by_type[layer_type].sort(key=lambda x: x['layer_index'])
    
    return layers_by_type

def calculate_recursive_product(layers_by_type: Dict) -> Tuple[float, Dict]:
    """計算遞歸乘法鏈"""
    stages = [
        ('FOUNDATION', 'FOUNDATION'),
        ('AMPLIFICATION', 'AMPLIFICATION'),
        ('SYNERGY', 'SYNERGY'),
        ('RESONANCE', 'RESONANCE'),
        ('QUANTUM_ENTANGLE', 'QUANTUM_ENTANGLE'),
        ('META_COMPUTE', 'META_COMPUTE'),
    ]
    
    stage_results = {}
    overall_product = 1.0
    
    for stage_name, layer_type in stages:
        if layer_type in layers_by_type:
            layers = layers_by_type[layer_type]
            stage_product = 1.0
            factors = []
            
            for layer in layers:
                amp_factor = layer['amplification_factor']
                stage_product *= amp_factor
                factors.append(amp_factor)
            
            stage_results[stage_name] = {
                'layers': len(layers),
                'factors': factors,
                'product': stage_product
            }
            
            overall_product *= stage_product
    
    return overall_product, stage_results

def verify_formulas(stage_results: Dict) -> Dict:
    """驗證各階段公式的正確性"""
    verification = {}
    
    # Foundation: 1.0
    if 'FOUNDATION' in stage_results:
        expected = 1.0
        actual = stage_results['FOUNDATION']['product']
        verification['FOUNDATION'] = {
            'expected': expected,
            'actual': actual,
            'verified': abs(actual - expected) < 0.001
        }
    
    # Amplification: 2^(1+2+3+4+5) = 2^15 = 32,768
    if 'AMPLIFICATION' in stage_results:
        expected = 2**15
        actual = stage_results['AMPLIFICATION']['product']
        verification['AMPLIFICATION'] = {
            'formula': '2^15',
            'expected': expected,
            'actual': actual,
            'verified': abs(actual - expected) < 1
        }
    
    # Synergy: 3^(1+2+3+4) = 3^10 = 59,049
    if 'SYNERGY' in stage_results:
        expected = 3**10
        actual = stage_results['SYNERGY']['product']
        verification['SYNERGY'] = {
            'formula': '3^10',
            'expected': expected,
            'actual': actual,
            'verified': abs(actual - expected) < 1
        }
    
    # Resonance: 4^(1+2+3) = 4^6 = 4,096
    if 'RESONANCE' in stage_results:
        expected = 4**6
        actual = stage_results['RESONANCE']['product']
        verification['RESONANCE'] = {
            'formula': '4^6',
            'expected': expected,
            'actual': actual,
            'verified': abs(actual - expected) < 1
        }
    
    # Quantum: e^(1+2+3) ≈ 403.43
    if 'QUANTUM_ENTANGLE' in stage_results:
        expected = math.exp(6)
        actual = stage_results['QUANTUM_ENTANGLE']['product']
        verification['QUANTUM_ENTANGLE'] = {
            'formula': 'e^6',
            'expected': expected,
            'actual': actual,
            'verified': abs(actual - expected) < 1
        }
    
    # Meta-Compute: e^(1^1.5 + 2^1.5) ≈ 46.0
    if 'META_COMPUTE' in stage_results:
        expected = math.exp(1**1.5 + 2**1.5)
        actual = stage_results['META_COMPUTE']['product']
        verification['META_COMPUTE'] = {
            'formula': 'e^(1^1.5+2^1.5)',
            'expected': expected,
            'actual': actual,
            'verified': abs(actual - expected) < 1
        }
    
    return verification

def generate_report(overall_product: float, stage_results: Dict, verification: Dict) -> str:
    """生成詳細報告"""
    report = []
    report.append("=" * 100)
    report.append("遞歸超指數協同係數驗證 - 完整報告")
    report.append("Recursive Superexponential Synergy Coefficient Verification Report")
    report.append("=" * 100)
    report.append("")
    
    report.append("【1. 階段級乘積】")
    report.append("-" * 100)
    
    for stage_name in ['FOUNDATION', 'AMPLIFICATION', 'SYNERGY', 'RESONANCE', 'QUANTUM_ENTANGLE', 'META_COMPUTE']:
        if stage_name in stage_results:
            result = stage_results[stage_name]
            factors = result['factors']
            product = result['product']
            
            factors_str = ' × '.join(f"{f:.4g}" for f in factors)
            report.append(f"\n{stage_name}:")
            report.append(f"  Factors: {factors_str}")
            report.append(f"  Product: {product:.6e}")
            
            if stage_name in verification:
                v = verification[stage_name]
                report.append(f"  Expected: {v.get('expected', 'N/A'):.6e}")
                report.append(f"  Verified: {'✅' if v['verified'] else '❌'}")
    
    report.append("\n" + "=" * 100)
    report.append("【2. 遞歸乘法鏈結果】")
    report.append("-" * 100)
    report.append(f"\nOverall Recursive Product: {overall_product:.6e}")
    report.append(f"Expected ES Multiplier:   1.44e+15")
    report.append(f"System Multiplier:        1.57e+22")
    
    ratio = overall_product / 1.44e15
    report.append(f"\nRatio (Actual/Expected): {ratio:.2f}x")
    
    if 0.99 < ratio < 1.01:
        report.append("✅ Within expected range (99%-101%)")
    else:
        report.append(f"⚠️  Outside expected range")
    
    report.append("\n" + "=" * 100)
    report.append("【3. 系統集成影響】")
    report.append("-" * 100)
    
    original_quintenary = 1.57e22
    new_quintenary = 1.0 * overall_product * 100 * 72500 * 1.0 * 1.5
    
    report.append(f"\nOriginal Quintenary Multiplier: {original_quintenary:.6e}")
    report.append(f"New Quintenary Multiplier:      {new_quintenary:.6e}")
    report.append(f"Increase Factor:                {new_quintenary / original_quintenary:.2f}x")
    
    report.append("\n" + "=" * 100)
    report.append(f"Report Generated: {datetime.now().isoformat()}")
    report.append("=" * 100)
    
    return "\n".join(report)

def main():
    """主函數"""
    print("Loading ES system state...")
    state = load_es_system_state()
    
    print("Analyzing layer configurations...")
    layers_by_type = analyze_layers(state)
    
    print("Calculating recursive product...")
    overall_product, stage_results = calculate_recursive_product(layers_by_type)
    
    print("Verifying formulas...")
    verification = verify_formulas(stage_results)
    
    print("\nGenerating report...")
    report = generate_report(overall_product, stage_results, verification)
    
    # 輸出到控制台
    print("\n" + report)
    
    # 保存到文件
    report_file = Path("/workspaces/cosmic-ai.uk/verification_recursive_synergy_report.txt")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ Report saved to: {report_file}")
    
    # 返回結果供進一步處理
    return {
        'overall_product': overall_product,
        'stage_results': stage_results,
        'verification': verification
    }

if __name__ == "__main__":
    result = main()
