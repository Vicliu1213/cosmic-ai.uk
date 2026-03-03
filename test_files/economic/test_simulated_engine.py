# internal/pkg/metrics.py
from prometheus_client import Counter, Histogram, Gauge

trade_counter = Counter('trades_total', 'Total number of trades executed', ['symbol', 'side'])
trade_duration = Histogram('trade_duration_seconds', 'Time taken to execute a trade')
account_balance = Gauge('account_balance', 'Current account balance')
