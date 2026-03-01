import ray
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

@ray.remote
class ConsensusManager:
    """宇宙共識管理系統 - 支持多種共識算法"""
    
    def __init__(self, consensus_config: Dict[str, Any], agents: List[Any]):
        self.config = consensus_config
        self.agents = agents
        self.algorithm = consensus_config.get('algorithm', 'weighted_voting')
        self.voting_threshold = float(consensus_config.get('voting_threshold', 0.5))
        self.decision_history = []
        self.voting_records = []
        
        print(f"共識管理器啟動，演算法: {self.algorithm}, 閾值: {self.voting_threshold}")

    def propose_and_vote(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """提案投票系統"""
        if self.algorithm == "weighted_voting":
            return self._weighted_voting(proposal)
        elif self.algorithm == "quantum_consensus":
            return self._quantum_consensus(proposal)
        elif self.algorithm == "delegated_voting":
            return self._delegated_voting(proposal)
        elif self.algorithm == "rank_choice":
            return self._rank_choice_voting(proposal)
        else:
            return {"error": f"不支援的演算法: {self.algorithm}"}

    def _weighted_voting(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """加權投票"""
        try:
            vote_refs = [agent.vote.remote(proposal) for agent in self.agents]
            results = ray.get(vote_refs)
            
            total_weight = 0.0
            approve_weight = 0.0
            
            for r in results:
                weight = float(r.get("weight", 1.0)) * self.config.get("default_vote_weight", 1.0)
                total_weight += weight
                if r.get("decision") == "approve":
                    approve_weight += weight
            
            approval_rate = approve_weight / total_weight if total_weight > 0 else 0
            passed = approval_rate >= self.voting_threshold
            
            vote_record = {
                'proposal': proposal,
                'algorithm': 'weighted_voting',
                'passed': passed,
                'approval_rate': approval_rate,
                'approve_weight': approve_weight,
                'total_weight': total_weight,
                'votes': results,
                'timestamp': datetime.now().isoformat()
            }
            
            self.voting_records.append(vote_record)
            self.decision_history.append(vote_record)
            
            return vote_record
        except Exception as e:
            return {"error": str(e), "proposal": proposal}

    def _quantum_consensus(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """量子共識機制"""
        try:
            vote_refs = [agent.vote.remote(proposal) for agent in self.agents]
            results = ray.get(vote_refs)
            
            # 計算量子態疊加
            approve_count = sum(1 for r in results if r.get("decision") == "approve")
            total_count = len(results)
            
            # 量子概率
            quantum_probability = approve_count / total_count if total_count > 0 else 0
            
            # 量子隧穿效應 - 允許小概率通過
            effective_threshold = self.voting_threshold - 0.05
            passed = quantum_probability >= effective_threshold
            
            return {
                'proposal': proposal,
                'algorithm': 'quantum_consensus',
                'passed': passed,
                'quantum_probability': quantum_probability,
                'approve_count': approve_count,
                'total_count': total_count,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "proposal": proposal}

    def _delegated_voting(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """委託投票 - 允許代理將投票權委託給他人"""
        try:
            vote_refs = [agent.vote.remote(proposal) for agent in self.agents]
            results = ray.get(vote_refs)
            
            # 實現委託邏輯
            effective_votes = []
            for i, r in enumerate(results):
                confidence = r.get('confidence', 0.5)
                weight = r.get('weight', 1.0) * confidence
                effective_votes.append({
                    'agent_id': r.get('agent_id'),
                    'decision': r.get('decision'),
                    'effective_weight': weight
                })
            
            total_weight = sum(v['effective_weight'] for v in effective_votes)
            approve_weight = sum(v['effective_weight'] for v in effective_votes 
                               if v['decision'] == 'approve')
            
            approval_rate = approve_weight / total_weight if total_weight > 0 else 0
            passed = approval_rate >= self.voting_threshold
            
            return {
                'proposal': proposal,
                'algorithm': 'delegated_voting',
                'passed': passed,
                'approval_rate': approval_rate,
                'effective_votes': effective_votes,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "proposal": proposal}

    def _rank_choice_voting(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """排名選擇投票"""
        try:
            vote_refs = [agent.vote.remote(proposal) for agent in self.agents]
            results = ray.get(vote_refs)
            
            # 計算首選票
            first_choice = sum(1 for r in results if r.get("decision") == "approve")
            total = len(results)
            
            # 計算多輪次投票
            approval_rate = first_choice / total if total > 0 else 0
            passed = approval_rate >= self.voting_threshold
            
            return {
                'proposal': proposal,
                'algorithm': 'rank_choice_voting',
                'passed': passed,
                'first_choice_approval': first_choice,
                'approval_rate': approval_rate,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "proposal": proposal}

    def get_voting_statistics(self) -> Dict[str, Any]:
        """取得投票統計"""
        if not self.voting_records:
            return {'message': '無投票記錄'}
        
        total_votes = len(self.voting_records)
        passed_votes = sum(1 for v in self.voting_records if v.get('passed'))
        avg_approval_rate = sum(v.get('approval_rate', 0) for v in self.voting_records) / total_votes
        
        return {
            'total_votes': total_votes,
            'passed_votes': passed_votes,
            'failed_votes': total_votes - passed_votes,
            'pass_rate': passed_votes / total_votes if total_votes > 0 else 0,
            'avg_approval_rate': avg_approval_rate,
            'algorithms_used': list(set(v.get('algorithm') for v in self.voting_records))
        }

    def export_voting_records(self, filepath: str):
        """匯出投票記錄"""
        export_data = {
            'config': self.config,
            'statistics': self.get_voting_statistics(),
            'records': self.voting_records[-100:],  # 最後100筆
            'timestamp': datetime.now().isoformat()
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
