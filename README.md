# Microservices Monitoring & Tracing Project

A comprehensive microservices monitoring and tracing system using Prometheus, Grafana, Loki, Tempo, and Alertmanager.

## 📁 Project Structure

```
sharing-monitoring-tracing/
├── app/                    # Main application
│   ├── main.py
│   └── requirements.txt
├── config/                 # Configuration files
│   ├── alertmanager.yml    # Alertmanager configuration
│   ├── alerts.yml          # Prometheus alert rules
│   ├── prometheus.yml      # Prometheus configuration
│   ├── loki-config.yaml    # Loki configuration
│   ├── promtail-config.yaml # Promtail configuration
│   ├── tempo.yaml          # Tempo configuration
│   ├── otel-collector-config.yaml # OpenTelemetry collector config
│   └── grafana/            # Grafana provisioning
│       ├── dashboards/     # Dashboard definitions
│       └── provisioning/   # Datasource and dashboard provisioning
├── docker/                 # Dockerfiles for all services
│   ├── Dockerfile.app
│   ├── Dockerfile.auth-service
│   ├── Dockerfile.user-service
│   ├── Dockerfile.order-service
│   ├── Dockerfile.payment-service
│   ├── Dockerfile.inventory-service
│   ├── Dockerfile.shipping-service
│   ├── Dockerfile.notification-service
│   └── Dockerfile.review-service
├── docs/                   # Documentation
│   ├── README_ERROR_SCENARIO.md
│   ├── SCENARIO_2_FLOW.md
│   └── HOW_TO_SEARCH_TRACE.md
├── scripts/                # Utility scripts
│   ├── check_*.py          # Health check scripts
│   ├── generate_traffic.py # Traffic generation
│   ├── trigger_*.py        # Error scenario triggers
│   ├── final_check.py      # Final verification
│   ├── start.bat           # Windows startup script
│   ├── start.sh            # Linux/Mac startup script
│   └── setup_and_test.bat  # Setup and test script
├── tests/                  # Test files
│   ├── test_*.py           # All test scripts
├── services/               # Microservices source code
│   ├── auth-service/
│   ├── user-service/
│   ├── order-service/
│   ├── payment-service/
│   ├── inventory-service/
│   ├── shipping-service/
│   ├── notification-service/
│   └── review-service/
├── logs/                   # Application logs
├── docker-compose.yml      # Docker Compose configuration
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+

### Start All Services

**Windows:**
```bash
scripts\start.bat
```

**Linux/Mac:**
```bash
chmod +x scripts/start.sh
./scripts/start.sh
```

**Or manually:**
```bash
docker-compose up -d
```

### Access Services

- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Tempo**: http://localhost:3200
- **Loki**: http://localhost:3100
- **Alertmanager**: http://localhost:9093

### Microservices

- **User Service**: http://localhost:8000
- **Order Service**: http://localhost:8001
- **Payment Service**: http://localhost:8002
- **Inventory Service**: http://localhost:8003
- **Shipping Service**: http://localhost:8004
- **Notification Service**: http://localhost:8005
- **Review Service**: http://localhost:8006
- **Auth Service**: http://localhost:8007

## 📝 Usage

### Generate Traffic

```bash
python scripts/generate_traffic.py
```

### Check Metrics

```bash
python scripts/check_metrics.py
```

### Test Luồng Thực Tế

```bash
python scripts/setup_and_test.bat
# Or manually:
python tests/test_real_flow.py
```

Test này sẽ mô phỏng luồng thực tế: Request → Error → Trace → Logs → Dashboard

### Run Test

```bash
# Test luồng thực tế (Request → Error → Trace → Logs → Dashboard)
python tests/test_real_flow.py
```

## 🔧 Configuration

All configuration files are located in the `config/` directory:

- **Prometheus**: `config/prometheus.yml` - Metrics collection and alert rules
- **Alertmanager**: `config/alertmanager.yml` - Alert routing and notifications
- **Grafana**: `config/grafana/` - Dashboards and datasource provisioning
- **Loki**: `config/loki-config.yaml` - Log aggregation configuration
- **Tempo**: `config/tempo.yaml` - Distributed tracing configuration

## 📚 Documentation

See the `docs/` directory for detailed documentation:

- `README_ERROR_SCENARIO.md` - Error scenario testing guide
- `SCENARIO_2_FLOW.md` - Scenario flow documentation
- `HOW_TO_SEARCH_TRACE.md` - Guide for searching traces

## 🛠️ Development

### Rebuild Services

```bash
docker-compose up -d --build <service-name>
```

### View Logs

```bash
docker-compose logs -f <service-name>
```

### Stop Services

```bash
docker-compose down
```

## 📊 Monitoring Stack

- **Prometheus**: Metrics collection and alerting
- **Grafana**: Visualization and dashboards
- **Loki**: Log aggregation
- **Tempo**: Distributed tracing
- **Alertmanager**: Alert management and routing

## 🔍 Troubleshooting

1. Check service health: `python scripts/check_alert_status.py`
2. Check firing alerts: `python scripts/check_firing_alerts.py`
3. Check metrics: `python scripts/check_metrics.py`
4. View logs: `docker-compose logs -f`

For more detailed troubleshooting, see `docs/README_ERROR_SCENARIO.md`.

