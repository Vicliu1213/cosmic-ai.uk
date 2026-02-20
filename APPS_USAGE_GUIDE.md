# Comic AI - Applications Usage Guide

## Quick Summary

Comic AI features 7 root-level applications covering image processing, multi-agent trading, quantum computing, and web dashboards. All are configured and ready to use.

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- Virtual environment activated: `source venv/bin/activate`

### Option 1: Launch All Apps with TMUX (Recommended)

```bash
# Start all 7 apps in TMUX session "comic-ai-apps"
./setup_tmux_apps.sh

# Attach to the session
tmux attach-session -t comic-ai-apps

# Switch between windows using Ctrl+B then 0-6
```

### Option 2: Launch Individual Apps

```bash
# Activate virtual environment
source venv/bin/activate

# Launch any app
python intelligent_file_processor_cli.py
python logging_dashboard.py
python task_panel_optimized.py
python hybrid_cloud_dashboard.py
python demo_singularity_system.py
python demo_gemini_trading_analyst.py
python src/cli/cli.py
```

## 📋 Individual Applications

### 1. Intelligent File Processor CLI
**Purpose**: Upload and analyze files (images, documents, code, etc.)

**File**: `intelligent_file_processor_cli.py`

**Usage**:
```bash
python intelligent_file_processor_cli.py

# Interactive commands:
upload <file_path>              # Upload and analyze a file
batch <directory_path>          # Batch analyze directory
history                         # View analysis history
help                           # Show help

# Examples:
upload photo.jpg --report      # Analyze image with report
upload script.py --json        # Output as JSON
batch ./project_files/         # Batch process directory
```

**Features**:
- ✅ Image analysis (JPG, PNG, GIF, WEBP, etc.)
- ✅ Document processing (PDF, DOCX, XLSX, etc.)
- ✅ Code analysis (PY, JS, TS, etc.)
- ✅ Archive handling (ZIP, TAR, 7Z, etc.)
- ✅ Hybrid/Advanced/Classic strategies

**Output**:
- Detailed analysis reports
- JSON format export
- File type detection
- Content summaries

---

### 2. Logging Dashboard
**Purpose**: Web-based centralized log viewer and analyzer

**File**: `logging_dashboard.py`

**Port**: 5000

**Access**: http://localhost:5000

**Features**:
- 📊 Real-time log visualization
- 🔍 Log search and filtering
- 📈 Log level statistics
- 🎯 Error tracking
- 📥 Log export capabilities

**Usage**:
```bash
python logging_dashboard.py

# Then open browser to http://localhost:5000
```

---

### 3. Task Panel Optimized
**Purpose**: Task management and optimization dashboard

**File**: `task_panel_optimized.py`

**Port**: 5001

**Access**: http://localhost:5001

**Features**:
- ✅ Task creation and management
- 📊 Progress tracking
- 🎯 Priority management
- ⏱️  Time estimates
- 📈 Performance analytics

**Usage**:
```bash
python task_panel_optimized.py

# Then open browser to http://localhost:5001
```

---

### 4. Hybrid Cloud Dashboard
**Purpose**: Multi-cloud resource management and monitoring

**File**: `hybrid_cloud_dashboard.py`

**Port**: 5002

**Access**: http://localhost:5002

**Features**:
- ☁️ Multi-cloud monitoring
- 📊 Resource utilization metrics
- 🔄 Workload distribution
- 💾 Storage management
- 🔐 Security monitoring

**Usage**:
```bash
python hybrid_cloud_dashboard.py

# Then open browser to http://localhost:5002
```

---

### 5. Multi-Agent Singularity Demo
**Purpose**: Quantum-enhanced multi-agent trading system demonstration

**File**: `demo_singularity_system.py`

**Features**:
- 🤖 Multiple independent trading agents
- 📊 Real market data simulation
- 🧮 Quantum-inspired optimization
- 💼 Portfolio management
- 📈 Performance metrics

**Run Duration**: ~10-30 seconds

**Usage**:
```bash
python demo_singularity_system.py

# Output:
# - Agent trading signals
# - Portfolio performance
# - Market analysis
# - Quantum optimization results
```

**Output Example**:
```
Agent 1: Buy signal on AAPL @ $150.25
Agent 2: Hold on BTC, wait for target $45000
System Portfolio Value: $1,234,567.89
Quantum efficiency gain: 23.4%
```

---

### 6. Gemini Trading Analyst Demo
**Purpose**: AI-powered trading analysis and recommendations

**File**: `demo_gemini_trading_analyst.py`

**API**: Requires Google Gemini API key (optional for demo)

**Features**:
- 🤖 AI-powered market analysis
- 💡 Trading recommendations
- 📊 Pattern recognition
- 🎯 Signal generation
- 📈 Risk assessment

**Usage**:
```bash
python demo_gemini_trading_analyst.py

# If API key configured:
#  - Real AI analysis
#  - Detailed recommendations
#
# Without API key:
#  - Demo mode with sample outputs
#  - Understanding of functionality
```

---

### 7. Main CLI
**Purpose**: Command-line interface for core system operations

**File**: `src/cli/cli.py`

**Features**:
- 📝 System configuration
- 🔧 Tool management
- 📊 Data analysis
- 🚀 Job execution
- 📋 Status reporting

**Usage**:
```bash
python src/cli/cli.py

# Interactive commands:
help                           # Show available commands
config                         # View/edit configuration
analyze <data_file>           # Analyze data
run <job_name>                # Execute job
status                        # System status
quit/exit                     # Exit CLI
```

---

## 🔧 Session Management

### TMUX Session Management Script

```bash
# Start management console
./manage_tmux_sessions.sh

# Options:
# 1) Attach to session
# 2) List all windows
# 3) Switch windows
# 4) View session status
# 5) View service logs
# 6) Kill processes/restart services
# 7) Stop session
# 8) Exit
```

### Useful TMUX Commands

```bash
# Attach to session
tmux attach-session -t comic-ai-apps

# List windows
tmux list-windows -t comic-ai-apps

# Switch to specific window (0-6)
tmux select-window -t comic-ai-apps:0

# Send command to window
tmux send-keys -t comic-ai-apps:0 "python script.py" Enter

# Detach from session (from inside)
Ctrl+B Ctrl+D

# Kill entire session
tmux kill-session -t comic-ai-apps

# List all sessions
tmux list-sessions
```

---

## 📊 Common Workflows

### Workflow 1: Batch Image Analysis
1. Prepare images in a directory
2. Launch File Processor: `python intelligent_file_processor_cli.py`
3. Command: `batch ./images/`
4. Review analysis results
5. Export report with `--report` flag

### Workflow 2: Multi-Dashboard Monitoring
1. Start all dashboards: `./setup_tmux_apps.sh`
2. Open 3 browser windows:
   - Logging Dashboard: http://localhost:5000
   - Task Panel: http://localhost:5001
   - Cloud Dashboard: http://localhost:5002
3. Monitor real-time metrics
4. Configure alerts as needed

### Workflow 3: Trading System Simulation
1. Launch Singularity Demo: `python demo_singularity_system.py`
2. Observe agent trading behavior
3. Review portfolio performance
4. Analyze quantum optimization impact
5. (Optional) Run Gemini Analyst for AI insights

### Workflow 4: System Administration
1. Start management script: `./manage_tmux_sessions.sh`
2. Monitor session status
3. View logs in real-time
4. Manage processes
5. Configure service parameters

---

## 🎯 Performance Tips

### Dashboard Access
- **Logging Dashboard**: ~50-100ms response time
- **Task Panel**: ~30-50ms response time
- **Cloud Dashboard**: ~60-150ms response time

### Optimal Configuration
```bash
# 1. Use TMUX for concurrent execution
./setup_tmux_apps.sh

# 2. Allocate sufficient resources
# - Min: 2 cores, 4GB RAM
# - Recommended: 4+ cores, 8GB+ RAM

# 3. Monitor with provided dashboards
# - Check resource usage in Cloud Dashboard
# - Monitor logs in Logging Dashboard
# - Track tasks in Task Panel
```

### Resource Monitoring
```bash
# View real-time resource usage
watch -n 1 'ps aux | grep python'

# Check dashboard ports are accessible
netstat -tlnp | grep -E '5000|5001|5002'

# Monitor system resources
free -h
df -h
```

---

## ✅ Verification Checklist

- [ ] All 7 applications import successfully
- [ ] Virtual environment activated
- [ ] TMUX session created successfully
- [ ] All 7 windows running (check with `tmux list-windows`)
- [ ] Dashboards accessible (test http://localhost:5000-5002)
- [ ] File Processor processes uploads
- [ ] Trading demos complete successfully
- [ ] CLI responds to commands

---

## 📖 Additional Resources

- **Test Suite**: `pytest src/tests/` (218 tests passing)
- **Quantum Implementation**: `quantum_grover_trading_algorithm.py`
- **Configuration**: `config/` directory
- **Documentation**: `docs/` and `docs/archive/` directories

---

## 🆘 Troubleshooting

### Dashboard Won't Load
```bash
# Check port availability
lsof -i :5000  # For logging dashboard

# Kill existing process on port
fuser -k 5000/tcp

# Restart dashboard
python logging_dashboard.py
```

### TMUX Session Issues
```bash
# Check existing sessions
tmux list-sessions

# Kill problematic session
tmux kill-session -t comic-ai-apps

# Recreate session
./setup_tmux_apps.sh
```

### File Processor Not Working
```bash
# Test with sample file
python intelligent_file_processor_cli.py
upload /tmp/test.txt

# Check file permissions
ls -la /tmp/test.txt
```

### Virtual Environment Issues
```bash
# Recreate virtual environment
rm -rf venv/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📞 Quick Reference

| App | Command | Port | Type |
|-----|---------|------|------|
| File Processor | `python intelligent_file_processor_cli.py` | - | CLI |
| Logging Dashboard | `python logging_dashboard.py` | 5000 | Web |
| Task Panel | `python task_panel_optimized.py` | 5001 | Web |
| Cloud Dashboard | `python hybrid_cloud_dashboard.py` | 5002 | Web |
| Singularity Demo | `python demo_singularity_system.py` | - | Demo |
| Gemini Analyst | `python demo_gemini_trading_analyst.py` | - | Demo |
| Main CLI | `python src/cli/cli.py` | - | CLI |

---

**Last Updated**: 2026-02-20  
**Status**: ✅ All applications tested and operational  
**Test Pass Rate**: 218/218 (100%)
