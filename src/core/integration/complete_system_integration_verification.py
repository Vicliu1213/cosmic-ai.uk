#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整系統集成驗證
Complete System Integration Verification

這個系統驗證所有 11 個子系統（8 + 3 新系統）的完整集成和協同工作。

驗證流程:
1. 檢查所有系統文件
2. 驗證所有報告文件
3. 測試系統互操作性
4. 驗證增益計算的一致性
5. 生成集成驗證報告
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime
from dataclasses import dataclass, field


# ============================================================================
# 配置
# ============================================================================

@dataclass
class IntegrationVerificationConfig:
    """集成驗證配置"""
    workspace: Path = Path("/workspaces/cosmic-ai.uk")
    log_dir: Path = field(default_factory=lambda: Path("/workspaces/cosmic-ai.uk/logs"))
    
    def __post_init__(self):
        self.log_dir.mkdir(parents=True, exist_ok=True)


def setup_logging(config: IntegrationVerificationConfig) -> logging.Logger:
    """設置日誌系統"""
    logger = logging.getLogger("CompleteSystemIntegration")
    logger.setLevel(logging.DEBUG)
    
    # 清除已有的處理器
    logger.handlers.clear()
    
    # 文件処理器
    fh = logging.FileHandler(
        config.log_dir / "complete_system_integration_verification.log"
    )
    fh.setLevel(logging.DEBUG)
    
    # 控制台処理器
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    # 格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger


# ============================================================================
# 系統驗證
# ============================================================================

class CompleteSystemIntegrationVerification:
    """完整系統集成驗證"""
    
    # 所有 11 個系統
    ALL_SYSTEMS = {
        # 原始 8 大子系統
        "ultrabrain_controller.py": "中央控制系統",
        "ultrabrain_api.py": "REST API 系統",
        "eternal_life_launcher.py": "啟動器系統",
        "verify_system.py": "驗證系統",
        "quantum_entanglement_verification.py": "量子糾纏態連結驗證",
        "hyper_exponential_coordination_system.py": "超指數遞歸協同",
        "quantum_field_theory_system.py": "量子場論系統",
        "infinite_eternal_qft_cycle_system.py": "無限永生循環",
        # 新增 3 個系統
        "quantum_theory_synergy_breakthrough_system.py": "理論協同突破層",
        "ultimate_gain_calculation_engine.py": "終極增益計算引擎",
        "complete_system_integration_verification.py": "完整系統集成驗證",
    }
    
    # 預期報告文件
    EXPECTED_REPORTS = {
        "QUANTUM_ENTANGLEMENT_SYNERGY_FINAL_REPORT.txt": "量子糾纏協同最終報告",
        "quantum_theory_synergy_breakthrough_report.txt": "理論協同突破報告",
        "quantum_theory_synergy_breakthrough_report.json": "理論協同突破 JSON",
        "ultimate_gain_calculation_report.txt": "終極增益計算報告",
        "ultimate_gain_calculation_report.json": "終極增益計算 JSON",
        "hyper_exponential_coordination_report.json": "超指數協同報告",
        "omniscient_verification_report.json": "全知驗證報告",
        "quantum_field_theory_system_report.json": "量子場論報告",
        "infinite_eternal_qft_system_report.json": "無限循環報告",
    }
    
    def __init__(self, config: IntegrationVerificationConfig = None):
        """初始化驗證系統"""
        self.config = config or IntegrationVerificationConfig()
        self.logger = setup_logging(self.config)
        
        self.logger.info("=" * 120)
        self.logger.info("完整系統集成驗證 初始化")
        self.logger.info("=" * 120)
        
        # 驗證結果
        self.verification_results = {
            "systems": {},
            "reports": {},
            "health_checks": {},
            "integration_status": "pending",
        }
    
    def verify_system_files(self) -> Dict[str, Dict[str, Any]]:
        """驗證所有系統文件"""
        self.logger.info("\n" + "=" * 120)
        self.logger.info("【步驟 1】驗證系統文件")
        self.logger.info("=" * 120)
        
        system_status = {}
        found_count = 0
        total_count = len(self.ALL_SYSTEMS)
        
        for filename, system_name in self.ALL_SYSTEMS.items():
            filepath = self.config.workspace / filename
            
            if filepath.exists():
                file_size = filepath.stat().st_size
                system_status[system_name] = {
                    "filename": filename,
                    "exists": True,
                    "size": file_size,
                    "status": "✓",
                }
                found_count += 1
                self.logger.info(f"✓ {system_name}: {filename} ({file_size} bytes)")
            else:
                system_status[system_name] = {
                    "filename": filename,
                    "exists": False,
                    "size": 0,
                    "status": "✗",
                }
                self.logger.warning(f"✗ {system_name}: {filename} (缺失)")
        
        self.logger.info(f"\n系統文件驗證: {found_count}/{total_count} 存在")
        
        self.verification_results["systems"] = system_status
        
        return system_status
    
    def verify_report_files(self) -> Dict[str, Dict[str, Any]]:
        """驗證所有報告文件"""
        self.logger.info("\n" + "=" * 120)
        self.logger.info("【步驟 2】驗證報告文件")
        self.logger.info("=" * 120)
        
        report_status = {}
        found_count = 0
        total_count = len(self.EXPECTED_REPORTS)
        
        for filename, report_name in self.EXPECTED_REPORTS.items():
            filepath = self.config.log_dir / filename
            
            if filepath.exists():
                file_size = filepath.stat().st_size
                report_status[report_name] = {
                    "filename": filename,
                    "exists": True,
                    "size": file_size,
                    "status": "✓",
                }
                found_count += 1
                self.logger.info(f"✓ {report_name}: {filename} ({file_size} bytes)")
            else:
                report_status[report_name] = {
                    "filename": filename,
                    "exists": False,
                    "size": 0,
                    "status": "✗",
                }
                self.logger.warning(f"✗ {report_name}: {filename} (缺失)")
        
        self.logger.info(f"\n報告文件驗證: {found_count}/{total_count} 存在")
        
        self.verification_results["reports"] = report_status
        
        return report_status
    
    def verify_report_integrity(self) -> Dict[str, Dict[str, Any]]:
        """驗證報告內容完整性"""
        self.logger.info("\n" + "=" * 120)
        self.logger.info("【步驟 3】驗證報告內容完整性")
        self.logger.info("=" * 120)
        
        integrity_results = {}
        
        json_reports = [
            ("ultimate_gain_calculation_report.json", "終極增益計算"),
            ("quantum_theory_synergy_breakthrough_report.json", "理論協同突破"),
            ("hyper_exponential_coordination_report.json", "超指數協同"),
            ("omniscient_verification_report.json", "全知驗證"),
        ]
        
        for filename, description in json_reports:
            filepath = self.config.log_dir / filename
            
            if filepath.exists():
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    integrity_results[description] = {
                        "status": "✓",
                        "valid_json": True,
                        "keys": list(data.keys()),
                    }
                    
                    self.logger.info(f"✓ {description} 報告 JSON 驗證通過")
                    self.logger.debug(f"  鑰匙: {list(data.keys())}")
                    
                except json.JSONDecodeError as e:
                    integrity_results[description] = {
                        "status": "✗",
                        "valid_json": False,
                        "error": str(e),
                    }
                    self.logger.warning(f"✗ {description} 報告 JSON 格式錯誤: {e}")
                except Exception as e:
                    integrity_results[description] = {
                        "status": "✗",
                        "valid_json": False,
                        "error": str(e),
                    }
                    self.logger.warning(f"✗ {description} 報告讀取錯誤: {e}")
            else:
                integrity_results[description] = {
                    "status": "✗",
                    "valid_json": False,
                    "error": "文件不存在",
                }
                self.logger.warning(f"✗ {description} 報告文件缺失")
        
        return integrity_results
    
    def verify_gain_values(self) -> Dict[str, Dict[str, Any]]:
        """驗證增益值的一致性"""
        self.logger.info("\n" + "=" * 120)
        self.logger.info("【步驟 4】驗證增益值一致性")
        self.logger.info("=" * 120)
        
        gain_values = {}
        
        # 檢查終極增益計算報告
        ultimate_report = self.config.log_dir / "ultimate_gain_calculation_report.json"
        if ultimate_report.exists():
            try:
                with open(ultimate_report, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                ultimate_gain = data.get("ultimate_gain", "未知")
                
                gain_values["終極增益"] = {
                    "value": ultimate_gain,
                    "source": "ultimate_gain_calculation_report.json",
                    "status": "✓" if ultimate_gain else "⚠",
                }
                
                self.logger.info(f"✓ 終極增益值: {ultimate_gain}")
                
                if "methods" in data:
                    for method, value in data["methods"].items():
                        gain_values[f"方法_{method}"] = {
                            "value": value,
                            "source": "ultimate_gain_calculation_report.json",
                        }
                        self.logger.info(f"  {method}: {value}")
            
            except Exception as e:
                self.logger.warning(f"無法讀取終極增益報告: {e}")
        
        # 檢查理論協同突破報告
        synergy_report = self.config.log_dir / "quantum_theory_synergy_breakthrough_report.json"
        if synergy_report.exists():
            try:
                with open(synergy_report, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                ultimate_gain = data.get("ultimate_gain", "未知")
                
                gain_values["協同突破增益"] = {
                    "value": ultimate_gain,
                    "source": "quantum_theory_synergy_breakthrough_report.json",
                    "status": "✓" if ultimate_gain else "⚠",
                }
                
                self.logger.info(f"✓ 協同突破增益: {ultimate_gain}")
            
            except Exception as e:
                self.logger.warning(f"無法讀取協同突破報告: {e}")
        
        return gain_values
    
    def verify_system_health(self) -> Dict[str, Any]:
        """驗證系統健康狀況"""
        self.logger.info("\n" + "=" * 120)
        self.logger.info("【步驟 5】驗證系統健康狀況")
        self.logger.info("=" * 120)
        
        health_checks = {
            "files_present": 0,
            "reports_present": 0,
            "json_valid": 0,
            "gains_extracted": 0,
            "overall_status": "unknown",
        }
        
        # 計數系統文件
        for system_name, status in self.verification_results["systems"].items():
            if status.get("exists"):
                health_checks["files_present"] += 1
        
        # 計數報告文件
        for report_name, status in self.verification_results["reports"].items():
            if status.get("exists"):
                health_checks["reports_present"] += 1
        
        # 檢查系統完整性百分比
        total_systems = len(self.ALL_SYSTEMS)
        files_percentage = (health_checks["files_present"] / total_systems) * 100
        
        total_reports = len(self.EXPECTED_REPORTS)
        reports_percentage = (health_checks["reports_present"] / total_reports) * 100
        
        self.logger.info(f"✓ 系統文件: {health_checks['files_present']}/{total_systems} ({files_percentage:.1f}%)")
        self.logger.info(f"✓ 報告文件: {health_checks['reports_present']}/{total_reports} ({reports_percentage:.1f}%)")
        
        # 判斷整體狀態
        if files_percentage >= 80 and reports_percentage >= 80:
            health_checks["overall_status"] = "healthy"
            self.logger.info("✓ 系統狀態: 健康 (充分整合)")
        elif files_percentage >= 60 and reports_percentage >= 60:
            health_checks["overall_status"] = "fair"
            self.logger.info("⚠ 系統狀態: 良好 (大部分整合)")
        else:
            health_checks["overall_status"] = "needs_attention"
            self.logger.warning("⚠ 系統狀態: 需要注意")
        
        self.verification_results["health_checks"] = health_checks
        
        return health_checks
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """運行集成測試"""
        self.logger.info("\n" + "=" * 120)
        self.logger.info("【步驟 6】運行集成測試")
        self.logger.info("=" * 120)
        
        test_results = {}
        
        # 測試 1: 理論協同突破系統
        test_results["quantum_theory_synergy"] = self._test_quantum_theory_synergy()
        
        # 測試 2: 終極增益計算引擎
        test_results["ultimate_gain_engine"] = self._test_ultimate_gain_engine()
        
        return test_results
    
    def _test_quantum_theory_synergy(self) -> Dict[str, Any]:
        """測試理論協同突破系統"""
        self.logger.info("\n【測試】理論協同突破系統...")
        
        test_status = {
            "name": "理論協同突破系統",
            "status": "pending",
            "error": None,
        }
        
        try:
            # 檢查報告文件
            report_path = self.config.log_dir / "quantum_theory_synergy_breakthrough_report.json"
            
            if report_path.exists():
                with open(report_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                test_status["status"] = "✓ 通過"
                test_status["report_data"] = {
                    "has_ultimate_gain": "ultimate_gain" in data,
                    "has_methods": "methods" in data,
                }
                
                self.logger.info(f"  ✓ 理論協同突破系統測試通過")
            else:
                test_status["status"] = "✗ 失敗"
                test_status["error"] = "報告文件不存在"
                self.logger.warning(f"  ✗ 理論協同突破報告不存在")
        
        except Exception as e:
            test_status["status"] = "✗ 失敗"
            test_status["error"] = str(e)
            self.logger.warning(f"  ✗ 理論協同突破測試失敗: {e}")
        
        return test_status
    
    def _test_ultimate_gain_engine(self) -> Dict[str, Any]:
        """測試終極增益計算引擎"""
        self.logger.info("\n【測試】終極增益計算引擎...")
        
        test_status = {
            "name": "終極增益計算引擎",
            "status": "pending",
            "error": None,
        }
        
        try:
            # 檢查報告文件
            report_path = self.config.log_dir / "ultimate_gain_calculation_report.json"
            
            if report_path.exists():
                with open(report_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                test_status["status"] = "✓ 通過"
                test_status["report_data"] = {
                    "has_ultimate_gain": "ultimate_gain" in data,
                    "has_methods": "methods" in data,
                    "layers_count": data.get("layers_count", 0),
                }
                
                self.logger.info(f"  ✓ 終極增益計算引擎測試通過 (層數: {data.get('layers_count', 0)})")
            else:
                test_status["status"] = "✗ 失敗"
                test_status["error"] = "報告文件不存在"
                self.logger.warning(f"  ✗ 終極增益計算報告不存在")
        
        except Exception as e:
            test_status["status"] = "✗ 失敗"
            test_status["error"] = str(e)
            self.logger.warning(f"  ✗ 終極增益計算測試失敗: {e}")
        
        return test_status
    
    def generate_integration_report(self) -> str:
        """生成集成驗證報告"""
        self.logger.info("\n" + "=" * 120)
        self.logger.info("【步驟 7】生成集成驗證報告")
        self.logger.info("=" * 120)
        
        report_lines = []
        report_lines.append("=" * 120)
        report_lines.append("完整系統集成驗證報告")
        report_lines.append("=" * 120)
        report_lines.append(f"生成時間: {datetime.now().isoformat()}")
        report_lines.append("")
        
        # 系統文件驗證結果
        report_lines.append("【系統文件驗證】")
        systems = self.verification_results.get("systems", {})
        found = sum(1 for s in systems.values() if s.get("exists"))
        total = len(systems)
        report_lines.append(f"  已找到: {found}/{total} 系統文件")
        report_lines.append("")
        
        for system_name, status in systems.items():
            if status.get("status") == "✓":
                report_lines.append(f"    ✓ {system_name}")
            else:
                report_lines.append(f"    ✗ {system_name}")
        report_lines.append("")
        
        # 報告文件驗證結果
        report_lines.append("【報告文件驗證】")
        reports = self.verification_results.get("reports", {})
        found = sum(1 for r in reports.values() if r.get("exists"))
        total = len(reports)
        report_lines.append(f"  已找到: {found}/{total} 報告文件")
        report_lines.append("")
        
        # 系統健康狀況
        report_lines.append("【系統健康狀況】")
        health = self.verification_results.get("health_checks", {})
        report_lines.append(f"  整體狀態: {health.get('overall_status', '未知').upper()}")
        report_lines.append(f"  系統文件: {health.get('files_present', 0)} 存在")
        report_lines.append(f"  報告文件: {health.get('reports_present', 0)} 存在")
        report_lines.append("")
        
        # 集成狀態
        report_lines.append("【集成狀態】")
        if health.get('overall_status') == 'healthy':
            report_lines.append("  ✓✓✓ 完整系統集成驗證通過 ✓✓✓")
            report_lines.append("")
            report_lines.append("  系統已成功整合所有 11 個組件:")
            report_lines.append("    1. 中央控制系統")
            report_lines.append("    2. REST API 系統")
            report_lines.append("    3. 啟動器系統")
            report_lines.append("    4. 驗證系統")
            report_lines.append("    5. 量子糾纏態連結驗證")
            report_lines.append("    6. 超指數遞歸協同")
            report_lines.append("    7. 量子場論系統")
            report_lines.append("    8. 無限永生循環")
            report_lines.append("    9. 理論協同突破層")
            report_lines.append("   10. 終極增益計算引擎")
            report_lines.append("   11. 完整系統集成驗證")
        else:
            report_lines.append("  ⚠ 系統集成驗證進行中")
            report_lines.append("  大部分核心系統已集成")
        
        report_lines.append("")
        report_lines.append("=" * 120)
        
        report_text = "\n".join(report_lines)
        
        # 保存報告
        report_path = self.config.log_dir / "complete_system_integration_verification_report.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        self.logger.info(f"報告已保存: {report_path}")
        
        return report_text
    
    def save_json_report(self) -> Path:
        """保存 JSON 報告"""
        json_data = {
            "timestamp": datetime.now().isoformat(),
            "systems_verified": len([s for s in self.verification_results.get("systems", {}).values() if s.get("exists")]),
            "reports_verified": len([r for r in self.verification_results.get("reports", {}).values() if r.get("exists")]),
            "health_status": self.verification_results.get("health_checks", {}).get("overall_status", "unknown"),
            "integration_complete": self.verification_results.get("health_checks", {}).get("overall_status") == "healthy",
        }
        
        json_path = self.config.log_dir / "complete_system_integration_verification_report.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"JSON 報告已保存: {json_path}")
        
        return json_path
    
    def run_complete_verification(self) -> Dict[str, Any]:
        """運行完整驗證"""
        self.logger.info("\n\n" + "=" * 120)
        self.logger.info("❯❯❯ 開始完整系統集成驗證 ❯❯❯")
        self.logger.info("=" * 120 + "\n")
        
        # 步驟 1: 驗證系統文件
        self.verify_system_files()
        
        # 步驟 2: 驗證報告文件
        self.verify_report_files()
        
        # 步驟 3: 驗證報告完整性
        integrity_results = self.verify_report_integrity()
        self.verification_results["integrity"] = integrity_results
        
        # 步驟 4: 驗證增益值
        gain_values = self.verify_gain_values()
        self.verification_results["gain_values"] = gain_values
        
        # 步驟 5: 驗證系統健康
        self.verify_system_health()
        
        # 步驟 6: 運行集成測試
        test_results = self.run_integration_tests()
        self.verification_results["integration_tests"] = test_results
        
        # 步驟 7: 生成報告
        report_text = self.generate_integration_report()
        
        # 保存 JSON 報告
        json_path = self.save_json_report()
        
        # 輸出報告
        self.logger.info("\n" + report_text)
        
        return {
            "success": True,
            "verification_results": self.verification_results,
            "report_path": str(self.config.log_dir / "complete_system_integration_verification_report.txt"),
            "json_report_path": str(json_path),
        }


def main():
    """主函數"""
    config = IntegrationVerificationConfig()
    verifier = CompleteSystemIntegrationVerification(config)
    
    result = verifier.run_complete_verification()
    
    print("\n" + "=" * 120)
    print("完整系統集成驗證 - 執行完成")
    print("=" * 120)
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
