@echo off

REM Create necessary directories
if not exist logs mkdir logs
if not exist config\grafana\provisioning\datasources mkdir config\grafana\provisioning\datasources
if not exist config\grafana\provisioning\dashboards mkdir config\grafana\provisioning\dashboards
if not exist config\grafana\dashboards mkdir config\grafana\dashboards

REM Start services
docker-compose up -d

echo.
echo Waiting for services to start...
timeout /t 10 /nobreak >nul

echo.
echo Services are starting up!
echo Grafana: http://localhost:3000 (admin/admin)
echo Prometheus: http://localhost:9090
echo Tempo: http://localhost:3200
echo Loki: http://localhost:3100
echo Alert Manager: http://localhost:9093
echo User Service: http://localhost:8000
echo Order Service: http://localhost:8001
echo Payment Service: http://localhost:8002
echo.
echo To view logs: docker-compose logs -f
echo To stop: docker-compose down

