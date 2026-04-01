class BasePlugin:
    def __init__(self, config):
        self.config = config
        self.features = []
        self.state = {}
        self.performance_history = []

    def receive_features(self, features):
        self.features = features

    def execute(self, data):
        raise NotImplementedError

    def feedback(self, result):
        """接收結果回饋（核心進化機制）"""
        self.performance_history.append(result)

    def adapt(self):
        """根據歷史表現調整策略"""
        if len(self.performance_history) > 10:
            avg = np.mean(self.performance_history)
            self.config.priority *= (1 + avg * 0.1)nj
