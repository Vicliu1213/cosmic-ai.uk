# 量子態技術文檔 (Quantum State Technical Documentation)

## 概述 (Overview)

本文檔提供量子態系統的完整技術規範，涵蓋兩種主要實現：
- **QuantumState**: 量子啟發式優化算法中的量子態表示
- **ClassicalQuantumState**: 增強型古典量子引擎中的古典量子態表示

---

## 1. QuantumState（量子啟發式量子態）

### 1.1 定義和結構

**來源文件**: `optimizer/hybrid_quantum_algorithm.py` (第 29-46 行)

```python
@dataclass
class QuantumState:
    """Quantum state representation for trading signals"""
    position: np.ndarray           # Current position in solution space
    amplitude: float               # Probability amplitude |ψ|²
    phase: float                   # Phase angle θ
    entanglement_measure: float    # Degree of entanglement with other states
    tunnel_probability: float      # Tunneling escape probability
    fitness: float = 0.0           # Objective function evaluation result
```

### 1.2 數據字段詳解

| 字段 | 類型 | 範圍 | 描述 |
|------|------|------|------|
| `position` | `np.ndarray` | ℝⁿ | 解空間中的當前位置，維度n根據優化問題而定 |
| `amplitude` | `float` | [0, 1] | 概率振幅，表示該量子態的存在概率，計算方式：P = amplitude² |
| `phase` | `float` | [0, 2π] | 量子相位角，控制量子態的方向和干涉性質 |
| `entanglement_measure` | `float` | [0, 1] | 與其他量子態的糾纏強度，1表示完全糾纏，0表示無糾纏 |
| `tunnel_probability` | `float` | [0, 1] | 量子隧穿逃逸概率，用於跳出局部最優 |
| `fitness` | `float` | (-∞, +∞) | 目標函數在此位置的評估值，值越大越優 |

### 1.3 核心方法

#### 1.3.1 get_probability()
```python
def get_probability(self) -> float:
    """Get probability from amplitude"""
    return self.amplitude ** 2
```
- **用途**: 從振幅計算實際概率
- **公式**: P(state) = |ψ|² = amplitude²
- **範圍**: [0, 1]
- **應用**: 波函數坍縮時確定測量結果的可能性

**示例**:
```python
state = QuantumState(
    position=np.array([1.0, 2.0, 3.0]),
    amplitude=0.707,  # 1/√2
    phase=np.pi/4,
    entanglement_measure=0.5,
    tunnel_probability=0.15
)
prob = state.get_probability()  # 0.5
```

#### 1.3.2 get_complex_amplitude()
```python
def get_complex_amplitude(self) -> complex:
    """Get complex amplitude representation"""
    return self.amplitude * np.exp(1j * self.phase)
```
- **用途**: 獲取複數形式的振幅
- **公式**: ψ = amplitude × e^(iθ) = amplitude × (cos θ + i sin θ)
- **應用**: 量子干涉計算、相位相關操作

**示例**:
```python
complex_amp = state.get_complex_amplitude()
# 如果 amplitude=1.0, phase=π/4
# 結果: 0.707 + 0.707i
```

### 1.4 狀態初始化

在 `HybridQuantumEnhancedAlgorithm._initialize_population()` 中初始化：

```python
def _initialize_population(self, bounds: List[Tuple[float, float]]) -> None:
    """Initialize quantum population with superposition states"""
    for _ in range(self.population_size):
        # 1. 解空間中的隨機位置
        position = np.array([
            np.random.uniform(b[0], b[1]) for b in bounds
        ])
        
        # 2. 統一疊加初始化
        amplitude = 1.0 / np.sqrt(self.population_size)  # 均勻疊加
        
        # 3. 隨機相位
        phase = np.random.uniform(0, 2 * np.pi)
        
        # 4. 創建量子態
        state = QuantumState(
            position=position,
            amplitude=amplitude,
            phase=phase,
            entanglement_measure=0.0,
            tunnel_probability=self.tunneling_probability
        )
        self.population.append(state)
```

**關鍵點**:
- 初始振幅 = 1/√(population_size)，確保概率歸一化
- 相位隨機分佈，增加初始多樣性
- 糾纏度初始為0（尚未與他態糾纏）

### 1.5 量子態演化

#### 1.5.1 Hadamard 門變換
```python
def _apply_hadamard(self, idx: int) -> None:
    """Hadamard gate: Create superposition of states"""
    state = self.population[idx]
    # Hadamard transformation: H|ψ⟩ = (|0⟩ + |1⟩)/√2
    perturbation = np.random.normal(0, 0.1, self.dimension)
    state.position = state.position + perturbation
    state.amplitude = state.amplitude / np.sqrt(2)  # 減半概率
```

**效果**: 
- 位置擾動：增加種群多樣性
- 振幅減半：增加疊加度

#### 1.5.2 Phase Shift 變換
```python
def _apply_phase_shift(self, idx: int) -> None:
    """Phase shift gate: Rotate phase angle"""
    state = self.population[idx]
    rotation_angle = np.random.uniform(-np.pi, np.pi)
    state.phase = (state.phase + rotation_angle) % (2 * np.pi)
    direction = np.exp(1j * state.phase).real
    state.position = state.position + direction * np.random.normal(0, 0.05, self.dimension)
```

**效果**:
- 相位旋轉：改變搜索方向
- 位置更新：沿相位指定方向移動

#### 1.5.3 Pauli-Z 門（相位翻轉）
```python
def _apply_pauli_z(self, idx: int) -> None:
    """Pauli-Z gate: Phase flip"""
    state = self.population[idx]
    # 通過當前最優解反射
    if self.best_state is not None:
        reflection_factor = 0.3
        state.position = self.best_state.position + reflection_factor * (
            self.best_state.position - state.position
        )
```

**效果**:
- 局部優化：向最優解靠近
- 逃逸機制：反射防止重複搜索

#### 1.5.4 CNOT 門（糾纏操作）
```python
def _apply_cnot(self, control: int, target: int) -> None:
    """CNOT gate: Creates entanglement"""
    control_state = self.population[control]
    target_state = self.population[target]
    
    if control_state.fitness > target_state.fitness:
        coupling = self.entanglement_strength
        target_state.position = (
            (1 - coupling) * target_state.position +
            coupling * control_state.position
        )
        target_state.entanglement_measure = self.entanglement_strength
```

**效果**:
- 優勝者吸引：好的解吸引較差的解
- 糾纏建立：目標態獲得糾纏度值

### 1.6 糾纏分析

```python
def _analyze_entanglement(self) -> None:
    """Analyze quantum entanglement in population"""
    for i, state_i in enumerate(self.population):
        entanglement_sum = 0.0
        
        for j, state_j in enumerate(self.population):
            if i != j:
                distance = euclidean(state_i.position, state_j.position)
                fitness_diff = abs(state_i.fitness - state_j.fitness)
                
                # 糾纏度 = e^(-distance) × 1/(1 + fitness_diff)
                entanglement = np.exp(-distance) * (1.0 / (1.0 + fitness_diff))
                entanglement_sum += entanglement
        
        state_i.entanglement_measure = entanglement_sum / (self.population_size - 1)
```

**計算原理**:
1. **距離依賴**: 解空間中相近的態更易糾纏
2. **適應度依賴**: 適應度相近的態更易糾纏
3. **歸一化**: 除以 (population_size - 1) 得到平均糾纏度

### 1.7 量子隧穿

```python
def _apply_quantum_tunneling(self) -> None:
    """Quantum tunneling: Escape local optima"""
    for state in self.population:
        effective_tunnel_prob = self.tunneling_probability * (
            1.0 + state.entanglement_measure
        )
        
        if np.random.random() < effective_tunnel_prob:
            jump_distance = np.random.exponential(0.2, self.dimension)
            direction = np.random.choice([-1, 1], self.dimension)
            state.position = state.position + jump_distance * direction
            state.phase = np.random.uniform(0, 2 * np.pi)
```

**特性**:
- 概率隨糾纏度增加而增加
- 跳躍距離遵循指數分佈
- 隨機方向保證多樣性

### 1.8 波函數坍縮（測量）

```python
def _measure_states(self) -> None:
    """Wave function collapse: Measure quantum states"""
    for state in self.population:
        # 概率歸一化
        total_amplitude = sum(s.amplitude for s in self.population)
        state.amplitude = state.amplitude / total_amplitude if total_amplitude > 0 else 1.0/np.sqrt(self.population_size)
        
        # 限制在 [0, 1]
        state.amplitude = np.clip(state.amplitude, 0, 1)
```

**說明**:
- 確保所有振幅之和為1（概率守恆）
- 相位在測量後保留（量子相干性）
- 位置為古典結果

---

## 2. ClassicalQuantumState（古典量子態）

### 2.1 定義和結構

**來源文件**: `engine/enhanced_quantum_engine.py` (第 33-41 行)

```python
@dataclass
class ClassicalQuantumState:
    """Classical Quantum State Representation"""
    state_vector: np.ndarray              # N維狀態向量
    probability_distribution: np.ndarray  # 概率分佈
    amplitude_coefficients: np.ndarray    # 振幅係數
    phase_information: np.ndarray         # 相位信息
    entropy: float                        # 信息熵
```

### 2.2 數據字段詳解

| 字段 | 類型 | 維度 | 描述 |
|------|------|------|------|
| `state_vector` | `np.ndarray` | (n,) | 狀態空間中的位置向量，n = StateSpaceOptimizer.dimension |
| `probability_distribution` | `np.ndarray` | (n,) | 歸一化概率分佈，Σ P_i = 1 |
| `amplitude_coefficients` | `np.ndarray` | (n,) | 各分量的振幅，計算為 \|state_vector\| |
| `phase_information` | `np.ndarray` | (n,) | 各分量的相位角，計算為 arg(state_vector) |
| `entropy` | `float` | 標量 | Shannon信息熵，H = -Σ P_i log(P_i) |

### 2.3 State Space Optimizer 方法

#### 2.3.1 初始化狀態
```python
def initialize_state(self, data: np.ndarray) -> ClassicalQuantumState:
    """Initialize quantum state using PCA for high-dimensional mapping"""
    
    # 步驟1: 數據標準化
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(data.reshape(-1, 1))
    
    # 步驟2: PCA降維
    pca = PCA(n_components=min(self.dimension, len(scaled_data)))
    state_vector = pca.fit_transform(scaled_data).flatten()
    
    # 步驟3: 概率分佈（非負化）
    abs_state = np.abs(state_vector)
    probability_dist = abs_state / np.sum(abs_state)
    
    # 步驟4: 計算振幅和相位
    amplitudes = np.abs(state_vector)
    phases = np.angle(state_vector + 1j * np.random.randn(len(state_vector)) * 0.01)
    
    # 步驟5: Shannon信息熵
    entropy = -np.sum(probability_dist * np.log(probability_dist + 1e-10))
    
    return ClassicalQuantumState(...)
```

**流程說明**:
1. **數據標準化**: 消除量綱，零均值單位方差
2. **PCA變換**: 從市場數據提取主要特徵
3. **非負化**: 確保概率非負
4. **相位隨機化**: 添加量子特性
5. **熵計算**: 衡量態的混亂度

**複雜度**: O(n²) 其中 n = len(data)

#### 2.3.2 態演化
```python
def evolve_state(self, gradient: np.ndarray) -> ClassicalQuantumState:
    """Evolve quantum state using gradient descent optimization"""
    
    # 梯度更新
    new_state_vector = self.current_state.state_vector - self.learning_rate * gradient
    
    # 歸一化
    norm = np.linalg.norm(new_state_vector)
    if norm > 0:
        new_state_vector = new_state_vector / norm
    
    # 更新概率分佈、相位、熵...
```

**算法**: 隨機梯度下降（SGD）
- **更新規則**: x_{t+1} = x_t - α∇f(x_t)
- **歸一化**: 保持單位向量（量子態性質）
- **學習率**: 預設 α = 0.01

#### 2.3.3 態測量
```python
def measure_state(self) -> Tuple[np.ndarray, float]:
    """Measure quantum state"""
    prob_dist = self.current_state.probability_distribution
    measurement_idx = np.random.choice(len(prob_dist), p=prob_dist)
    confidence = prob_dist[measurement_idx]
    return np.array([measurement_idx]), confidence
```

**過程**:
1. 根據概率分佈採樣
2. 返回測量結果索引和置信度
3. 模擬波函數坍縮

### 2.4 概率決策引擎

#### 2.4.1 相干性計算
```python
def calculate_coherence(self, signal_data: np.ndarray, reference: np.ndarray) -> float:
    """Calculate coherence using signal coherence function"""
    from scipy.signal import coherence as scipy_coherence
    f, coh = scipy_coherence(signal_data, reference, nperseg=min(len(signal_data)//2, 256))
    mean_coherence = np.mean(coh)
    return min(1.0, max(0.0, mean_coherence))
```

**用途**: 衡量兩個信號之間的相似度和同步性
- **範圍**: [0, 1]
- **含義**: 1 = 完全相干，0 = 無相關

**應用**: 市場信號一致性檢驗

#### 2.4.2 決策制定
```python
def make_decision(self, market_signal: Dict[str, float], coherence: float) -> Dict[str, Any]:
    """Make decision based on probability and coherence"""
    signal_strength = market_signal.get('strength', 0.5)
    decision_confidence = coherence * signal_strength
    should_execute = decision_confidence > self.coherence_threshold
    return {...}
```

**決策邏輯**:
- **置信度** = 相干性 × 信號強度
- **執行條件** = 置信度 > 閾值（預設 0.85）

### 2.5 相關性分析器

#### 2.5.1 糾纏強度計算
```python
@staticmethod
def calculate_entanglement_strength(variables: np.ndarray) -> float:
    """Calculate entanglement strength using Pearson correlation"""
    corr_matrix = np.corrcoef(variables.T)
    mask = ~np.eye(corr_matrix.shape[0], dtype=bool)
    entanglement = np.mean(np.abs(corr_matrix[mask]))
    return min(1.0, max(0.0, entanglement))
```

**公式**:
- **Pearson相關係數**: r = Cov(X,Y) / (σ_X σ_Y)
- **糾纏度**: 非對角線相關係數的平均絕對值

#### 2.5.2 互信息計算
```python
@staticmethod
def calculate_mutual_information(x: np.ndarray, y: np.ndarray, bins: int = 10) -> float:
    """Calculate mutual information"""
    # 直方圖聯合分佈
    hist_xy, _, _ = np.histogram2d(x, y, bins=bins)
    # 邊際分佈
    hist_x, _ = np.histogram(x, bins=bins)
    hist_y, _ = np.histogram(y, bins=bins)
    # 互信息: I(X;Y) = Σ p(x,y) log(p(x,y) / (p(x)p(y)))
    mi = np.sum(pxy[mask] * np.log(pxy[mask] / (px_py[mask] + 1e-10)))
    return max(0.0, mi)
```

**意義**: 衡量兩個變數共享的信息量

### 2.6 增強信號處理器

#### 2.6.1 共振頻率計算
```python
@staticmethod
def calculate_resonance_frequency(market_data: np.ndarray, fs: float = 100) -> Tuple[float, float]:
    """Calculate resonance frequency using FFT"""
    fft_result = np.fft.fft(market_data)
    power_spectrum = np.abs(fft_result) ** 2
    frequencies = np.fft.fftfreq(len(market_data), 1/fs)
    peak_idx = np.argmax(power_spectrum[:len(power_spectrum)//2])
    resonance_freq = abs(frequencies[peak_idx])
    resonance_strength = power_spectrum[peak_idx] / np.sum(power_spectrum)
    return resonance_freq, resonance_strength
```

**步驟**:
1. 傅立葉變換提取頻域信息
2. 計算功率譜密度
3. 找到峰值頻率
4. 計算歸一化強度

#### 2.6.2 共振濾波
```python
@staticmethod
def apply_resonance_filter(data: np.ndarray, resonance_freq: float, 
                          quality_factor: float = 10.0) -> np.ndarray:
    """Apply resonance filter using bandpass"""
    # 帶通濾波: 中心頻率 ± 帶寬/2
    normalized_freq = resonance_freq / nyquist_freq
    bandwidth = normalized_freq / quality_factor
    low_freq = max(0.001, normalized_freq - bandwidth / 2)
    high_freq = min(0.999, normalized_freq + bandwidth / 2)
    b, a = signal.butter(4, [low_freq, high_freq], btype='band')
    filtered_data = signal.filtfilt(b, a, data)
    return filtered_data
```

---

## 3. 量子態在交易系統中的應用

### 3.1 QuantumEnhancedSignalGenerator 集成

```python
def generate_quantum_signal(
    self,
    price_data: np.ndarray,
    volume_data: np.ndarray,
    volatility: float
) -> Dict[str, Any]:
    """Generate trading signal using quantum-enhanced optimization"""
    
    # 定義目標函數
    def signal_quality(params: np.ndarray) -> float:
        momentum = (price_data[-1] - price_data[-5]) / price_data[-5]
        avg_volume = np.mean(volume_data[-self.market_lookback:])
        volume_signal = current_volume / avg_volume
        signal = (params[0] * momentum + 
                 params[1] * (volume_signal - 1.0) +
                 params[2] * volatility)
        return 1.0 / (1.0 + np.exp(-signal))  # Sigmoid
    
    # 使用混合量子算法優化參數
    bounds = [(0.0, 1.0), (0.0, 1.0), (0.0, 1.0)]
    result = self.algo.optimize(signal_quality, bounds)
    
    # 生成量子信號指標
    return {
        'signal_strength': result['best_fitness'],
        'quantum_phase': result['best_phase'],
        'quantum_entanglement': result['best_entanglement'],
        'amplitude_probability': result['best_amplitude'] ** 2,
        'convergence_rate': result['convergence_rate'],
        'quantum_confidence': base_signal * (1.0 + result['best_entanglement'])
    }
```

### 3.2 QuantumEnsemblePredictor 集成

```python
def predict_ensemble(self, market_features: Dict[str, np.ndarray]) -> Dict[str, Any]:
    """Generate ensemble prediction from multiple quantum optimizers"""
    
    predictions = []
    quantum_phases = []
    entanglements = []
    
    # 運行多個量子優化器
    for predictor in self.predictors:
        result = predictor.optimize(feature_objective, bounds)
        predictions.append(result['best_fitness'])
        quantum_phases.append(result['best_phase'])
        entanglements.append(result['best_entanglement'])
    
    # 量子平均（考慮相位相干性）
    avg_prediction = np.mean(predictions)
    phase_vector = np.array(quantum_phases)
    coherence = np.abs(np.mean(np.exp(1j * phase_vector)))  # 相干性
    weighted_prediction = avg_prediction * (0.5 + 0.5 * coherence)
    
    return {
        'ensemble_prediction': weighted_prediction,
        'quantum_coherence': coherence,
        'prediction_confidence': weighted_prediction * (0.5 + 0.5 * np.mean(entanglements))
    }
```

---

## 4. 性能指標

### 4.1 計算複雜度

| 操作 | 時間複雜度 | 空間複雜度 | 說明 |
|------|-----------|-----------|------|
| 初始化 | O(p) | O(p×n) | p=population_size, n=dimension |
| Hadamard門 | O(n) | O(n) | 向量擾動 |
| Phase Shift | O(n) | O(n) | 複數運算 |
| Entanglement分析 | O(p²×n) | O(p) | 配對比較 |
| 量子隧穿 | O(p×n) | O(n) | 指數採樣 |
| 波函數坍縮 | O(p) | O(1) | 歸一化 |

### 4.2 精度指標

| 指標 | 典型值 | 說明 |
|------|--------|------|
| 振幅歸一化誤差 | < 1e-10 | 概率守恆精度 |
| 相位精度 | ±1e-6 弧度 | 相干性保持 |
| 糾纏度範圍 | [0, 1] | 確保物理合理性 |
| 熵計算誤差 | < 1e-8 | 數值穩定性 |

### 4.3 收斂性分析

```python
def _calculate_convergence_rate(self) -> float:
    """Calculate convergence rate"""
    first_fitness = self.iteration_history[0]['best_fitness']
    last_fitness = self.iteration_history[-1]['best_fitness']
    return (last_fitness - first_fitness) / abs(first_fitness)
```

**收斂速度因素**:
- 量子隧穿概率增加 → 收斂速度快
- 糾纏度高 → 種群多樣性降低
- 相位對齐 → 搜索方向一致性強

---

## 5. 最佳實踐

### 5.1 初始化建議

```python
# 適當的初始參數設置
algo = HybridQuantumEnhancedAlgorithm(
    population_size=50,        # 平衡探索和利用
    quantum_gates=10,          # 每迭代的量子操作數
    entanglement_strength=0.8, # 強糾纏促進收斂
    tunneling_probability=0.15,# 適度逃逸
    max_iterations=100         # 足夠的迭代次數
)
```

### 5.2 超參數調優

| 參數 | 範圍 | 影響 |
|------|------|------|
| population_size | 20-100 | 增大→精度↑但速度↓ |
| quantum_gates | 5-20 | 增大→探索↑收斂↓ |
| entanglement_strength | 0.3-0.9 | 增大→收斂↑但易陷入局部最優 |
| tunneling_probability | 0.05-0.3 | 增大→逃逸↑但不穩定 |

### 5.3 監控檢查點

在優化過程中監控：

```python
for iteration in self.iteration_history:
    print(f"Iter {iteration['iteration']}:")
    print(f"  Best Fitness: {iteration['best_fitness']:.6f}")
    print(f"  Avg Entanglement: {iteration['avg_entanglement']:.4f}")
    print(f"  Avg Phase: {iteration['avg_phase']:.4f}")
```

**檢查點**:
- 適應度單調遞增
- 糾纏度穩定
- 相位多樣化

---

## 6. 故障排查

### 6.1 常見問題

**問題1**: 振幅溢出 (Amplitude Overflow)
```
症狀: amplitude > 1 或 < 0
原因: 缺乏歸一化
解決: 調用 _measure_states() 進行歸一化
```

**問題2**: 相位不連續
```
症狀: phase 在 π 和 -π 之間跳躍
原因: 沒有模 2π 運算
解決: 使用 phase = (phase + delta) % (2 * np.pi)
```

**問題3**: 糾纏度過高
```
症狀: entanglement_measure ≈ 1 （種群退化）
原因: entanglement_strength 過大
解決: 減小 CNOT 門中的 coupling 係數
```

### 6.2 數值穩定性

```python
# 防止數值問題
amplitude = np.clip(amplitude, 0, 1)
distance = np.clip(distance, 1e-10, 1e10)
entropy = -np.sum(prob_dist * np.log(prob_dist + 1e-10))  # 避免 log(0)
```

---

## 7. 參考資源

### 代碼文件
- `optimizer/hybrid_quantum_algorithm.py` - QuantumState 實現
- `engine/enhanced_quantum_engine.py` - ClassicalQuantumState 實現
- `src/core/enhanced_quantum_market_analyzer.py` - 交易應用集成

### 相關文檔
- `docs/01_quantum_entanglement_system.md` - 量子糾纏系統
- `docs/03_quantum_field_theory_system.md` - 量子場論
- `docs/09_unified_superexponential_theory.md` - 統一超指數理論

### 測試文件
- `src/tests/test_quantum_grover_integration.py` - 量子算法測試
- `src/tests/test_optimizers.py` - 優化器測試

---

## 8. 版本歷史

| 版本 | 日期 | 變更 |
|------|------|------|
| 1.0 | 2026-03-01 | 初始版本，覆蓋核心量子態概念和實現 |

---

**文檔維護者**: OpenCode Agent  
**最後更新**: 2026-03-01  
**狀態**: ✅ 完成
