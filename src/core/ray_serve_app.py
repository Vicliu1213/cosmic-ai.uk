"""
Ray Serve 應用 - 量子優化服務
"""

from ray import serve
from quantum_dashboard import QuantumDashboard
import json

app = serve.Application()

@serve.deployment
class QuantumOptimizationService:
    """量子優化服務"""
    
    def __init__(self):
        self.dashboard = QuantumDashboard()
    
    @serve.batch(max_batch_size=10)
    async def __call__(self, requests):
        """處理優化請求"""
        results = []
        for request in requests:
            if self.dashboard.report:
                results.append({
                    "status": "success",
                    "data": self.dashboard.report
                })
            else:
                results.append({
                    "status": "error",
                    "message": "No optimization data available"
                })
        return results

app = QuantumOptimizationService.bind()
