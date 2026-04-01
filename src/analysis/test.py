"""
Phase 2 模块测试：使用模拟数据验证各组件。
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from forest_analyzer import ForestAnalyzer
from singularity import SingularityDetector
from multiframe import MultiFrameAnalyzer
from signal_generator import SignalGenerator

# 生成模拟OHLCV数据
def generate_mock_data(days=100, freq='1H'):
    idx = pd.date_range(start=datetime.now() - timedelta(days=days), periods=days*24, freq=freq)
    close = 50000 + np.cumsum(np.random.randn(len(idx)) * 100)
    high = close + np.random.rand(len(idx)) * 200
    low = close - np.random.rand(len(idx)) * 200
    volume = np.random.randint(1000, 10000, size=len(idx))
    df = pd.DataFrame({'open': close, 'high': high, 'low': low, 'close': close, 'volume': volume}, index=idx)
    return df

def main():
    print("Phase 2 测试开始...")

    # 1. 生成数据
    df_1h = generate_mock_data(days=30, freq='1H')
    df_4h = df_1h.resample('4H').agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'}).dropna()
    df_1d = df_1h.resample('1D').agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'}).dropna()
    data_dict = {'1h': df_1h, '4h': df_4h, '1d': df_1d}

    # 2. 多时间框架分析
    mf = MultiFrameAnalyzer()
    mf_result = mf.analyze(data_dict)
    print("多时间框架分析结果:")
    print(mf_result)

    # 3. 训练森林模型
    forest = ForestAnalyzer()
    forest.train(df_1h)
    print("\n特征重要性:")
    print(forest.feature_importances_)

    # 4. 预测最新信号
    forest_result = forest.predict(df_1h)
    print("\n森林预测结果:")
    print(forest_result)

    # 5. 奇点检测
    sd = SingularityDetector()
    # 准备技术指标（简单示例）
    technical = {'rsi': 75}  # 实际应从计算中获得
    singularity_prob = sd.detect(df_1h, technical)
    print(f"\n奇点概率: {singularity_prob:.4f}")

    # 6. 生成信号
    gen = SignalGenerator()
    signals = gen.generate(mf_result, forest_result, singularity_prob, df_1h['close'].iloc[-1])
    print("\n生成信号:")
    for s in signals:
        print(f"  {s.signal_type} 信号, 强度={s.strength.name}, 置信度={s.confidence:.2%}, 仓位={s.recommended_position:.2%}")

    print("\nPhase 2 测试完成。")

if __name__ == "__main__":
    main()l
