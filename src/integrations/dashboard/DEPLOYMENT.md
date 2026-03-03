# LLM-TradeBot Cosmic Panel - Deployment Guide

## Quick Start (Development)

### 1. Install Dependencies
```bash
pip install fastapi uvicorn websockets aiohttp python-dotenv pyyaml
```

### 2. Start the Server
```bash
cd /workspaces/cosmic-ai.uk/src/integrations/dashboard
python main.py
```

Server will start on `http://localhost:8000`

### 3. Access the Dashboard
- **Web UI**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## Environment Configuration

Create a `.env` file in the dashboard directory:

```env
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=INFO
```

## API Quick Reference

### Health Check
```bash
curl http://localhost:8000/api/health
```

### Get Agents
```bash
curl http://localhost:8000/api/agents/summary
```

### Add Cosmic Signal
```bash
curl -X POST http://localhost:8000/api/signals/cosmic \
  -H "Content-Type: application/json" \
  -d '{
    "signal_type": "BUY",
    "symbol": "BTCUSDT",
    "confidence": 0.85,
    "source": "cosmic"
  }'
```

### Update Agent
```bash
curl -X POST http://localhost:8000/api/agents/trend_agent_1/update \
  -H "Content-Type: application/json" \
  -d '{
    "status": "RUNNING",
    "current_analysis": "Uptrend detected"
  }'
```

### Update Trading Metrics
```bash
curl -X POST http://localhost:8000/api/metrics/trading \
  -H "Content-Type: application/json" \
  -d '{
    "sharpe_ratio": 3.2,
    "win_rate": 0.65,
    "total_pnl": 1250.50,
    "max_drawdown": -0.12
  }'
```

### Control System
```bash
# Start
curl -X POST http://localhost:8000/api/control/start

# Pause
curl -X POST http://localhost:8000/api/control/pause

# Stop
curl -X POST http://localhost:8000/api/control/stop

# Reset
curl -X POST http://localhost:8000/api/control/reset
```

## Docker Deployment

### Build Docker Image
```bash
docker build -t llm-tradebot-cosmic-panel:latest .
```

### Run in Container
```bash
docker run -p 8000:8000 \
  -e PORT=8000 \
  -e HOST=0.0.0.0 \
  llm-tradebot-cosmic-panel:latest
```

### Docker Compose
```yaml
version: '3.8'
services:
  panel:
    build: .
    ports:
      - "8000:8000"
    environment:
      PORT: 8000
      HOST: 0.0.0.0
      LOG_LEVEL: INFO
    restart: unless-stopped
```

## Kubernetes Deployment

### Create ConfigMap
```bash
kubectl create configmap panel-config \
  --from-literal=PORT=8000 \
  --from-literal=HOST=0.0.0.0
```

### Deploy
```bash
kubectl apply -f deployment.yaml
```

### Example deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-cosmic-panel
spec:
  replicas: 2
  selector:
    matchLabels:
      app: llm-cosmic-panel
  template:
    metadata:
      labels:
        app: llm-cosmic-panel
    spec:
      containers:
      - name: panel
        image: llm-tradebot-cosmic-panel:latest
        ports:
        - containerPort: 8000
        env:
        - name: PORT
          valueFrom:
            configMapKeyRef:
              name: panel-config
              key: PORT
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: llm-cosmic-panel
spec:
  selector:
    app: llm-cosmic-panel
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

## Production Checklist

### Security
- [ ] Restrict CORS origins (modify `allow_origins`)
- [ ] Add authentication (JWT or API keys)
- [ ] Setup SSL/TLS certificates
- [ ] Use environment variables for secrets
- [ ] Rate limiting enabled
- [ ] Request validation on all endpoints

### Performance
- [ ] Database optimization (switch from in-memory)
- [ ] Connection pooling configured
- [ ] Caching strategy implemented
- [ ] Load balancing setup
- [ ] Monitoring and alerting configured

### Reliability
- [ ] Error handling tested
- [ ] Logging comprehensive
- [ ] Graceful shutdown implemented
- [ ] Health checks configured
- [ ] Backup strategy in place

### Compliance
- [ ] Data retention policy set
- [ ] Audit logging enabled
- [ ] Privacy compliance checked
- [ ] Documentation updated

## Monitoring & Logs

### View Logs (Docker)
```bash
docker logs -f <container_id>
```

### View Logs (Kubernetes)
```bash
kubectl logs -f deployment/llm-cosmic-panel
```

### Log Levels
- `DEBUG`: Detailed diagnostics
- `INFO`: General information (default)
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical errors

### Prometheus Metrics (Future)
```bash
# Metrics endpoint will be available at:
http://localhost:8000/metrics
```

## Troubleshooting

### Server Won't Start
```bash
# Check port availability
lsof -i :8000

# Check dependencies
pip list | grep -E "fastapi|uvicorn"

# View startup logs
python main.py
```

### WebSocket Connection Issues
- Ensure WebSocket proxies are configured
- Check firewall rules for port 8000
- Verify CORS settings
- Test with `wscat`:
  ```bash
  pip install wscat
  wscat -c ws://localhost:8000/ws/live-updates
  ```

### Memory Issues
```bash
# Monitor memory usage
watch -n 1 'ps aux | grep python | grep main.py'

# Increase limit if needed
# Or implement database persistence
```

### CORS Errors
Update `main.py` CORS middleware:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Performance Tuning

### Uvicorn Workers
```bash
# Run with multiple workers
uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000
```

### Max Connections
Set in environment:
```bash
export UVICORN_MAX_CONNECTIONS=100
```

### Request Limits
Configure in code:
```python
# Limit request size
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["example.com"])
```

## Next Steps

1. **Phase 2**: Integrate with real LLM-TradeBot agent state
2. **Phase 3**: Add performance charts and advanced analytics
3. **Phase 4**: Setup production monitoring and scaling

## Support

For issues or questions:
- Check TEST_REPORT.md for test results
- Review README.md for API documentation
- Check server logs: `tail -f /tmp/panel_server.log`
