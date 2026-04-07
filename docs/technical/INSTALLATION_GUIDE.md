# 安装指南

本指南介绍如何安装和配置 Cosmic AI 系统。

## 系统要求

- Python 3.8+
- pip 或 conda
- Git
- 可选：Docker & Docker Compose

## 快速安装

### 1. 克隆仓库

```bash
git clone https://github.com/anomalyco/cosmic-ai.uk.git
cd cosmic-ai.uk
```

### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件并填入必要的 API 密钥和配置
```

### 5. 初始化数据库

```bash
python src/scripts/initialize_db.py
```

### 6. 验证安装

```bash
python src/scripts/system_check.py
```

## Docker 安装

### 构建 Docker 镜像

```bash
docker build -t cosmic-ai .
```

### 运行容器

```bash
docker run -d \
  -e GEMINI_API_KEY=your_key \
  -e REDIS_URL=redis://redis:6379 \
  -p 8000:8000 \
  cosmic-ai
```

## 详细配置

### API 密钥配置

- **Gemini API**: 参考 [GEMINI_API_INTEGRATION_GUIDE.md](GEMINI_API_INTEGRATION_GUIDE.md)
- **Vertex AI**: 参考 [VERTEX_AI_SETUP.md](VERTEX_AI_SETUP.md)

### 数据库配置

- **Redis**: 参考 [DATABASE_REDIS_AZURE_INTEGRATION.md](DATABASE_REDIS_AZURE_INTEGRATION.md)
- **Azure**: 参考 [DATABASE_REDIS_AZURE_INTEGRATION.md](DATABASE_REDIS_AZURE_INTEGRATION.md)

### 交易系统配置

- **Hummingbot**: 参考 [ETHANALGOX_HUMMINGBOT_INTEGRATION_GUIDE.md](ETHANALGOX_HUMMINGBOT_INTEGRATION_GUIDE.md)

## 故障排除

如遇到问题，请参考 [TROUBLESHOOTING_OPTIMIZATION.md](TROUBLESHOOTING_OPTIMIZATION.md)

## 下一步

- [快速开始指南](QUICK_REFERENCE.md)
- [系统设置](SETUP_ENGINE_GUIDE.md)
- [部署指南](DEPLOYMENT_MONITORING.md)
