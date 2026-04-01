# src/synergy_engine/cluster_synergy.py

class ClusterSynergyEngine:
    """
    策略集群協同引擎
    將策略分組，實現集群間的協同爆發
    """

    def __init__(self):
        self.clusters = {}
        self.cross_cluster_synergy = {}

    def create_clusters(self, strategies: List[str], cluster_size: int = 3):
        """
        將策略分組為集群

        每個集群內部實現 1+1+1 > 100 的協同
        集群之間實現 集群+集群 > 1000 的超協同
        """
        n_strategies = len(strategies)
        n_clusters = (n_strategies + cluster_size - 1) // cluster_size

        clusters = {}
        for i in range(n_clusters):
            start = i * cluster_size
            end = min(start + cluster_size, n_strategies)
            cluster_name = f"cluster_{i+1}"
            clusters[cluster_name] = strategies[start:end]

        self.clusters = clusters
        return clusters

    def calculate_cluster_synergy(self, cluster_results: Dict[str, float]) -> Dict:
        """
        計算集群間協同效應

        公式：Total = Σ(Cluster_Effect) × Π(Cross_Synergy)
        """
        # 1. 集群內部協同
        internal_effects = []
        for cluster_name, effect in cluster_results.items():
            internal_effects.append(effect)

        # 2. 集群間協同（指數級）
        n_clusters = len(internal_effects)
        cross_synergy = np.prod(internal_effects) ** (1 + 0.1 * n_clusters)

        # 3. 總協同效應
        total_effect = sum(internal_effects) * cross_synergy

        return {
            'internal_effects': internal_effects,
            'cross_synergy': cross_synergy,
            'total_effect': total_effect,
            'n_clusters': n_clusters,
            'synergy_multiplier': total_effect / (sum(internal_effects) + 1e-10)
        }
