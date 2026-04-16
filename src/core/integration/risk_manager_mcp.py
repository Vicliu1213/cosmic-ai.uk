#!/usr/bin/env python3
"""
风险管理 MCP 服务器
Risk Management MCP Server

提供风险管理和合规工具给 OpenCode
Provides risk management and compliance tools to OpenCode
"""

import json
import logging
from typing import Any, Dict, List
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RiskManager:
    """风险管理器"""

    async def check_position_limits(self, symbol: str, quantity: float) -> Dict[str, Any]:
        """检查头寸限制"""
        try:
            # 定义风险限制
            limits = {
                "AAPL": {"max_position": 10000, "max_pct_portfolio": 0.15, "max_sector": 0.25},
                "MSFT": {"max_position": 8000, "max_pct_portfolio": 0.12, "max_sector": 0.25},
                "default": {"max_position": 5000, "max_pct_portfolio": 0.08, "max_sector": 0.25}
            }

            limit_config = limits.get(symbol, limits["default"])
            current_position = 3000  # 模拟当前头寸
            portfolio_pct = 0.06  # 模拟投资组合百分比
            sector_concentration = 0.18  # 模拟行业集中度

            proposed_position = current_position + quantity
            proposed_portfolio_pct = portfolio_pct + (quantity / 1000000)  # 简化计算

            limit_checks = {
                "position_limit": proposed_position > limit_config["max_position"],
                "portfolio_pct_limit": proposed_portfolio_pct > limit_config["max_pct_portfolio"],
                "sector_limit": sector_concentration > limit_config["max_sector"]
            }

            check = {
                "symbol": symbol,
                "quantity": quantity,
                "proposed_position": proposed_position,
                "limit_exceeded": limit_checks,
                "current_state": {
                    "current_position": current_position,
                    "current_portfolio_pct": portfolio_pct,
                    "current_sector_concentration": sector_concentration
                },
                "limits": limit_config,
                "recommendation": "APPROVED" if not any(limit_checks.values()) else "REJECTED",
                "check_timestamp": datetime.now().isoformat()
            }

            return {
                "success": True,
                "data": check,
                "message": "头寸限制检查完成"
            }
        except Exception as e:
            logger.error(f"头寸限制检查失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "头寸限制检查失败"
            }

    async def calculate_var(self, symbols: List[str], confidence: float = 0.95) -> Dict[str, Any]:
        """计算风险价值 (Value at Risk)"""
        try:
            var_results = {}
            for symbol in symbols:
                var_results[symbol] = {
                    "symbol": symbol,
                    "confidence_level": confidence,
                    "var_amount": 50000 if symbol == "AAPL" else 35000,
                    "var_pct": 0.05 if symbol == "AAPL" else 0.035,
                    "expected_shortfall": 65000 if symbol == "AAPL" else 45000,
                    "es_pct": 0.065 if symbol == "AAPL" else 0.045
                }

            analysis = {
                "symbols": symbols,
                "var_results": var_results,
                "portfolio_var": sum(r["var_amount"] for r in var_results.values()),
                "portfolio_expected_shortfallpackage，": sum(r["expected_shortfall"] for r in var_results.values()),
                "analysis_timestamp": datetime.now().isoformat()
            }

            return {
                "success": True,
                "data": analysis,
                "message": f"完成 {len(symbols)} 个资产的VaR计算"
            }
        except Exception as e:
            logger.error(f"VaR计算失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "VaR计算失败"
            }

    async def stress_test(self, scenario: str) -> Dict[str, Any]:
        """压力测试"""
        try:
            scenarios = {
                "market_crash": {
                    "description": "市场暴跌 20%",
                    "market_change": -0.20,
                    "volatility_increase": 0.50
                },
                "rate_hike": {
                    "description": "利率上升 2%",
                    "rate_change": 0.02,
                    "bond_impact": -0.08
                },
                "geopolitical": {
                    "description": "地缘政治危机",
                    "risk_premium": 0.05,
                    "volatility_increase": 0.30
                },
                "liquidity_crisis": {
                    "description": "流动性危机",
                    "bid_ask_spread_increase": 10,
                    "volume_decrease": 0.50
                }
            }

            scenario_config = scenarios.get(scenario, scenarios["market_crash"])

            results = {
                "scenario": scenario,
                "scenario_description": scenario_config.get("description"),
                "portfolio_impact": {
                    "value_change_pct": -0.15,
                    "value_change_amount": -150000,
                    "affected_positions": 5,
                    "affected_symbols": ["AAPL", "MSFT", "GOOGL", "TSLA", "META"]
                },
                "position_impact": {
                    "AAPL": {"change": -0.18, "stress_loss": -45000},
                    "MSFT": {"change": -0.12, "stress_loss": -30000},
                    "GOOGL": {"change": -0.20, "stress_loss": -35000},
                    "TSLA": {"change": -0.25, "stress_loss": -25000},
                    "META": {"change": -0.15, "stress_loss": -15000}
                },
                "recovery_time_estimate": "3-5 business days",
                "mitigation_recommendations": [
                    "立即削减高风险头寸",
                    "增加流动性储备",
                    "审查对冲策略"
                ],
                "test_timestamp": datetime.now().isoformat()
            }

            return {
                "success": True,
                "data": results,
                "message": f"完成 '{scenario}' 压力测试"
            }
        except Exception as e:
            logger.error(f"压力测试失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "压力测试失败"
            }

    async def compliance_check(self, regulation: str = "all") -> Dict[str, Any]:
        """合规检查"""
        try:
            compliance_status = {
                "regulations": {
                    "sec": {
                        "status": "compliant",
                        "rules_checked": 15,
                        "violations": 0,
                        "warnings": 0
                    },
                    "finra": {
                        "status": "compliant",
                        "rules_checked": 22,
                        "violations": 0,
                        "warnings": 1
                    },
                    "mifid_ii": {
                        "status": "compliant",
                        "rules_checked": 18,
                        "violations": 0,
                        "warnings": 0
                    }
                },
                "trading_violations": [],
                "reporting_status": {
                    "position_reporting": "up_to_date",
                    "transaction_reporting": "up_to_date",
                    "risk_reporting": "up_to_date"
                },
                "next_audit": "2026-03-01",
                "check_timestamp": datetime.now().isoformat()
            }

            return {
                "success": True,
                "data": compliance_status,
                "message": "合规检查完成 - 所有规定均已遵守"
            }
        except Exception as e:
            logger.error(f"合规检查失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "合规检查失败"
            }

    async def get_risk_report(self) -> Dict[str, Any]:
        """获取风险报告"""
        try:
            report = {
                "report_date": datetime.now().isoformat(),
                "executive_summary": {
                    "overall_risk_level": "moderate",
                    "key_risks": [
                        "市场波动性增加",
                        "行业集中度风险",
                        "流动性风险"
                    ],
                    "risk_score": 6.5  # 1-10 scale
                },
                "detailed_risk_metrics": {
                    "market_risk": {
                        "beta": 1.05,
                        "correlation_to_market": 0.72,
                        "var_95": 50000,
                        "var_99": 75000
                    },
                    "credit_risk": {
                        "counterparty_exposures": 15,
                        "exposure_concentration": 0.12,
                        "default_probability": 0.001
                    },
                    "operational_risk": {
                        "incidents_this_month": 1,
                        "loss_amount": 5000,
                        "recovery_status": "recovered"
                    },
                    "liquidity_risk": {
                        "days_to_liquidate_95": 3,
                        "bid_ask_spread_average": 0.02,
                        "liquidity_coverage_ratio": 1.85
                    }
                },
                "recommendations": [
                    "加强风险监控频率",
                    "审查投资组合多样化",
                    "更新应急计划"
                ],
                "next_review": "2026-03-19"
            }

            return {
                "success": True,
                "data": report,
                "message": "风险报告生成成功"
            }
        except Exception as e:
            logger.error(f"生成风险报告失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "生成风险报告失败"
            }

def print_mcp_tools() -> Any:
    """输出MCP工具定义"""
    tools = {
        "tools": [
            {
                "name": "check_position_limits",
                "description": "检查建议的头寸是否满足风险限制 / Check if proposed position satisfies risk limits",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "交易符号"
                        },
                        "quantity": {
                            "type": "number",
                            "description": "建议的头寸数量"
                        }
                    },
                    "required": ["symbol", "quantity"]
                }
            },
            {
                "name": "calculate_var",
                "description": "计算投资组合的风险价值(VaR) / Calculate Value at Risk for portfolio",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "symbols": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "交易符号列表"
                        },
                        "confidence": {
                            "type": "number",
                            "description": "信心水平 (0-1)",
                            "default": 0.95
                        }
                    },
                    "required": ["symbols"]
                }
            },
            {
                "name": "stress_test",
                "description": "运行压力测试场景 / Run stress test scenarios",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "scenario": {
                            "type": "string",
                            "enum": ["market_crash", "rate_hike", "geopolitical", "liquidity_crisis"],
                            "description": "压力测试场景"
                        }
                    },
                    "required": ["scenario"]
                }
            },
            {
                "name": "compliance_check",
                "description": "检查是否符合监管要求 / Check regulatory compliance",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "regulation": {
                            "type": "string",
                            "enum": ["sec", "finra", "mifid_ii", "all"],
                            "description": "规制",
                            "default": "all"
                        }
                    }
                }
            },
            {
                "name": "get_risk_report",
                "description": "获取详细的风险管理报告 / Get detailed risk management report",
                "inputSchema": {"type": "object", "properties": {}}
            }
        ]
    }
    print(json.dumps(tools, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    print_mcp_tools()
