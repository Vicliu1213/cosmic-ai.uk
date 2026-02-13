# Comic AI - First-Time Deployment Guide

**Version**: 2.0.0  
**Last Updated**: 2026-02-13  
**Target Environment**: Production (cosmic-ai.uk)

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Environment Setup](#environment-setup)
3. [Configuration Setup](#configuration-setup)
4. [Database Initialization](#database-initialization)
5. [Dependency Installation](#dependency-installation)
6. [Service Configuration](#service-configuration)
7. [Validation & Testing](#validation--testing)
8. [Deployment to Production](#deployment-to-production)
9. [Post-Deployment Verification](#post-deployment-verification)
10. [Rollback Procedures](#rollback-procedures)
11. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Pre-Deployment Checklist

Before beginning deployment, verify all prerequisites are met:

### System Requirements

- [ ] Python 3.10+ installed (`python3 --version`)
- [ ] Redis server running (`redis-cli ping`)
- [ ] Nginx installed and configured
- [ ] Let's Encrypt SSL certificate obtained
- [ ] Git repository cloned to `/root/comic_ai`
- [ ] Minimum 4GB RAM available
- [ ] Minimum 20GB disk space available
- [ ] Internet connectivity for API calls

### Credentials & Secrets

- [ ] Google Cloud credentials obtained (Vertex AI)
- [ ] OpenAI API key obtained
- [ ] Binance API keys generated
- [ ] Telegram Bot token created
- [ ] Azure OpenAI credentials (if using)
- [ ] All credentials stored securely (not in git)

### Network & DNS

- [ ] Domain name: `cosmic-ai.uk` registered
- [ ] DNS A record pointing to server IP
- [ ] Firewall rules configured (ports 80, 443 open)
- [ ] SSL certificate ready at `/etc/letsencrypt/live/cosmic-ai.uk/`

---

## Environment Setup

### Step 1: Create Project Directory Structure

```bash
cd /root/comic_ai

# Verify directory structure
ls -la config/          # Should have: core/, services/, security/, deployment/
ls -la src/             # Should have: cli/, core/, plugins/, tests/, utils/
ls -la scripts/         # Should have: deployment scripts
```

### Step 2: Copy Environment Configuration Template

```bash
# Copy template to actual .env file
cp config/templates/.env.template .env

# Edit with actual values
nano .env
```

### Step 3: Set Environment Variables

Edit `.env` file with your actual values:

```bash
# System Configuration
COMIC_AI_ENV=production
COMIC_AI_VERSION=2.0.0
TIMEZONE=Asia/Hong_Kong
COMIC_AI_MAX_WORKERS=8
COMIC_AI_CACHE_SIZE=2GB

# API Keys (obtain from respective services)
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_CLOUD_PROJECT=your_gcp_project_id
VERTEX_AI_MODEL=claude-3-5-sonnet@20241022
VERTEX_AI_TEMPERATURE=0.7
VERTEX_AI_MAX_TOKENS=2048

# Database
DATABASE_TYPE=sqlite
DATABASE_PATH=data/comic_ai.db
REDIS_HOST=localhost
REDIS_PORT=6379

# Trading Configuration
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET_KEY=your_binance_secret_key
TRADING_MAX_POSITIONS=15
TRADING_RISK_PER_TRADE=0.02

# Notifications
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# Security
SECURITY_SSL_CERT_PATH=/etc/letsencrypt/live/cosmic-ai.uk/fullchain.pem
SECURITY_SSL_KEY_PATH=/etc/letsencrypt/live/cosmic-ai.uk/privkey.pem
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
```

### Step 4: Source Environment Variables

```bash
# Add to your shell profile (~/.bashrc or ~/.zshrc)
source /root/comic_ai/.env

# Or manually set for current session
set -a
source /root/comic_ai/.env
set +a

# Verify
echo $OPENAI_API_KEY  # Should not be empty
```

---

## Configuration Setup

### Step 1: Validate Configuration Files

```bash
# Run validation script
python3 scripts/validate_config.py

# Expected output:
# - All YAML files valid
# - Environment variables set
# - Services accessible
# - Security checks pass
```

### Step 2: Review Critical Configurations

```bash
# System configuration
cat config/core/main_system_config.yaml

# Trading configuration
cat config/services/trading_config.yaml

# Security settings
cat config/security/security_config.yaml

# Deployment settings
cat config/deployment/deployment_config.yaml
```

### Step 3: Configure Logging

```bash
# Logging configuration is in:
cat config/core/logging_config.yaml

# Create log directories
mkdir -p logs
mkdir -p logs/trading
mkdir -p logs/quantum
mkdir -p logs/api

# Set permissions
chmod 755 logs
```

---

## Database Initialization

### Step 1: Create Database Directory

```bash
# Create data directory
mkdir -p data
chmod 755 data

# Verify
ls -la data/
```

### Step 2: Initialize SQLite Database

```bash
# Create initial database
python3 << 'EOF'
import sqlite3
from pathlib import Path

db_path = Path('data/comic_ai.db')
db_path.parent.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Create tables (schema depends on your application)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS trading_positions (
        id INTEGER PRIMARY KEY,
        symbol TEXT NOT NULL,
        quantity REAL NOT NULL,
        entry_price REAL NOT NULL,
        entry_time TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS trading_history (
        id INTEGER PRIMARY KEY,
        symbol TEXT NOT NULL,
        action TEXT NOT NULL,
        quantity REAL NOT NULL,
        price REAL NOT NULL,
        timestamp TIMESTAMP NOT NULL,
        pnl REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS market_data (
        id INTEGER PRIMARY KEY,
        symbol TEXT NOT NULL,
        price REAL NOT NULL,
        volume REAL NOT NULL,
        timestamp TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

conn.commit()
conn.close()
print("✅ Database initialized successfully")
EOF
```

### Step 3: Verify Database

```bash
# Check database exists
ls -la data/comic_ai.db

# Verify tables created
sqlite3 data/comic_ai.db ".tables"

# Expected output: market_data trading_history trading_positions
```

---

## Dependency Installation

### Step 1: Update Package Manager

```bash
# Update pip
python3 -m pip install --upgrade pip

# Install build essentials (if needed)
apt-get update && apt-get install -y build-essential python3-dev
```

### Step 2: Install Python Dependencies

```bash
# Install from requirements.txt
pip install -r requirements.txt

# Verify key packages
python3 -c "import yaml; print('✅ PyYAML')"
python3 -c "import numpy; print('✅ NumPy')"
python3 -c "import redis; print('✅ Redis')"
python3 -c "from google.cloud import aiplatform; print('✅ Google Cloud')"
```

### Step 3: Verify Installation

```bash
# List installed packages
pip list | grep -E "yaml|numpy|redis|google|openai"

# Check for any missing dependencies
pip check
```

---

## Service Configuration

### Step 1: Configure Redis Cache

```bash
# Verify Redis is running
redis-cli ping
# Expected: PONG

# Check Redis configuration
redis-cli CONFIG GET maxmemory
redis-cli CONFIG GET maxmemory-policy

# Set up Redis persistence (if needed)
redis-cli CONFIG SET save "900 1 300 10 60 10000"
```

### Step 2: Configure Nginx Reverse Proxy

```bash
# Nginx configuration should already be at:
cat /etc/nginx/sites-available/cosmic-ai.uk

# Expected:
# - Listen on port 80 (HTTP)
# - Redirect to 443 (HTTPS)
# - Proxy to localhost:8083

# Test Nginx configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### Step 3: Configure SSL Certificate Auto-Renewal

```bash
# Verify certificate installed
ls -la /etc/letsencrypt/live/cosmic-ai.uk/

# Set up auto-renewal
sudo apt-get install certbot python3-certbot-nginx
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Test renewal (dry-run)
sudo certbot renew --dry-run
```

---

## Validation & Testing

### Step 1: Run Configuration Validation

```bash
# Comprehensive validation
python3 scripts/validate_config.py

# Expected: ✅ All checks pass (or document any failures)
```

### Step 2: Test Core Functionality

```bash
# Test imports
python3 << 'EOF'
from src.core.singularity_system import SingularitySystem
from src.core.quantum_market_analyzer import QuantumMarketAnalyzer
print("✅ Core imports successful")
EOF

# Test API connectivity
python3 << 'EOF'
import os
from google.cloud import aiplatform

# Test Vertex AI connection
project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
aiplatform.init(project=project_id, location=location)
print("✅ Vertex AI connection successful")
EOF
```

### Step 3: Run Unit Tests

```bash
# Run all tests
pytest -v

# Run specific test file
pytest src/tests/ktzen_test.py -v

# Check coverage (if available)
pytest --cov=src src/tests/
```

### Step 4: Test Service Connectivity

```bash
# Test Redis
redis-cli ping

# Test Database
sqlite3 data/comic_ai.db "SELECT COUNT(*) FROM trading_positions;"

# Test Nginx/SSL
curl -k https://127.0.0.1

# Test from external (after DNS setup)
curl -k https://cosmic-ai.uk
```

---

## Deployment to Production

### Step 1: Final Pre-Deployment Checks

```bash
# Verify all environment variables
python3 scripts/validate_config.py

# Expected: Configuration validation PASSED
```

### Step 2: Start Core Services

```bash
# Start Redis (if not already running)
redis-server --daemonize yes

# Start Nginx
sudo systemctl start nginx

# Verify services
sudo systemctl status nginx
redis-cli ping
```

### Step 3: Start Application Services

```bash
# Start Dashboard (port 8080)
python3 src/cli/cli.py --dashboard &

# Start Main HTTP Server (port 8083)
python3 -m http.server 8083 --directory . &

# Or use a process manager (recommended)
# supervisord -c supervisord.conf
```

### Step 4: Verify Deployment

```bash
# Check processes running
ps aux | grep python3

# Check ports listening
netstat -tlnp | grep -E "8080|8083|443|6379"

# Test application endpoints
curl https://cosmic-ai.uk
curl https://cosmic-ai.uk/api/status

# Monitor logs
tail -f logs/comic_ai.log
```

---

## Post-Deployment Verification

### Step 1: Monitor Application Health

```bash
# Check for errors in logs
grep -i error logs/*.log

# Monitor system resources
top -b -n 1 | head -20
free -h
df -h

# Check application status
curl https://cosmic-ai.uk/status
```

### Step 2: Verify All Components

- [ ] Dashboard accessible at `https://cosmic-ai.uk`
- [ ] Trading system initialized
- [ ] Quantum engine running
- [ ] API endpoints responding
- [ ] Redis cache working
- [ ] Database persisting data
- [ ] Logging functioning
- [ ] Alerts configured

### Step 3: Run Smoke Tests

```bash
# Test critical endpoints
python3 << 'EOF'
import requests
import json

base_url = "https://cosmic-ai.uk"

# Test endpoints
endpoints = [
    "/",
    "/api/status",
    "/api/health",
]

for endpoint in endpoints:
    try:
        response = requests.get(f"{base_url}{endpoint}", verify=False)
        print(f"{'✅' if response.status_code < 400 else '❌'} {endpoint}: {response.status_code}")
    except Exception as e:
        print(f"❌ {endpoint}: {e}")
EOF
```

---

## Rollback Procedures

### If Critical Error Occurs

```bash
# Stop all services
pkill -f "python3.*cli.py"
pkill -f "python3.*http.server"
sudo systemctl stop nginx
redis-cli shutdown

# Check logs for errors
tail -f logs/error.log

# Restore from backup
cp -r data/backup/comic_ai.db.bak data/comic_ai.db

# Restart services
redis-server --daemonize yes
sudo systemctl start nginx
# ... restart application services
```

### Configuration Rollback

```bash
# If config change caused issues
cp .env.backup .env
source .env

# Restart application
# ... restart all services
```

---

## Monitoring & Maintenance

### Daily Tasks

```bash
# Check logs for errors
grep ERROR logs/*.log

# Verify services running
ps aux | grep -E "python3|nginx|redis"

# Monitor disk usage
df -h

# Check database integrity
sqlite3 data/comic_ai.db "PRAGMA integrity_check;"
```

### Weekly Tasks

- [ ] Review trading logs and P&L
- [ ] Check system performance metrics
- [ ] Verify backups are running
- [ ] Review error logs and fix issues
- [ ] Update documentation if needed

### Monthly Tasks

- [ ] Database optimization (VACUUM)
- [ ] Log rotation and archival
- [ ] Security updates
- [ ] Performance review
- [ ] Capacity planning

### Commands Reference

```bash
# Database maintenance
sqlite3 data/comic_ai.db "VACUUM;"
sqlite3 data/comic_ai.db "ANALYZE;"

# Backup
tar -czf data/backup/comic_ai_$(date +%Y%m%d).tar.gz data/ config/ logs/

# Log rotation
logrotate -f /etc/logrotate.d/comic-ai

# Restart application
systemctl restart comic-ai
```

---

## Troubleshooting Guide

### Issue: Port Already in Use

```bash
# Find process using port
lsof -i :8083
# Kill process
kill -9 <PID>
```

### Issue: Redis Connection Failed

```bash
# Check Redis status
redis-cli ping
# Restart Redis
redis-server --daemonize yes
```

### Issue: SSL Certificate Error

```bash
# Verify certificate
openssl x509 -in /etc/letsencrypt/live/cosmic-ai.uk/fullchain.pem -text -noout
# Renew certificate
sudo certbot renew --force-renewal
```

### Issue: Database Locked

```bash
# Check open connections
sqlite3 data/comic_ai.db "SELECT * FROM pragma_database_list;"
# Restart application
pkill -f "python3"
```

---

## Support & Escalation

| Issue | Escalation | Contact |
|-------|-----------|---------|
| Configuration | Level 1 | Check CONFIG_SETUP_REPORT.md |
| Performance | Level 2 | Check monitoring dashboard |
| Security | Level 3 | Contact security team |
| Critical Outage | Level 4 | Emergency procedures |

---

## Success Criteria

Deployment is considered successful when:

✅ All services running and responding  
✅ Configuration validation passes  
✅ SSL certificate valid and renewed automatically  
✅ Database initialized and persisting data  
✅ Trading system operational  
✅ Logging functioning  
✅ Monitoring alerts configured  
✅ No critical errors in logs  
✅ Response times < 500ms  
✅ System resource usage normal  

---

**Document Version**: 1.0  
**Last Updated**: 2026-02-13  
**Next Review**: 2026-03-13
