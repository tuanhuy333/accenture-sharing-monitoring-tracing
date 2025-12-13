#!/bin/bash

# Create necessary directories
mkdir -p logs
mkdir -p config/grafana/provisioning/datasources
mkdir -p config/grafana/provisioning/dashboards
mkdir -p config/grafana/dashboards

# Start services
docker-compose up -d

echo "Waiting for services to start..."
sleep 10

echo ""
echo "Services are starting up!"
echo "Grafana: http://localhost:3000 (admin/admin)"
echo "Prometheus: http://localhost:9090"
echo "Tempo: http://localhost:3200"
echo "Loki: http://localhost:3100"
echo "Alert Manager: http://localhost:9093"
echo "User Service: http://localhost:8000"
echo "Order Service: http://localhost:8001"
echo "Payment Service: http://localhost:8002"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"

