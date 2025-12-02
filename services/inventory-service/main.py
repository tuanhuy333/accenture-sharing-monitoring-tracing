import os
import time
import random
import logging
import requests
from flask import Flask, jsonify, request
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from prometheus_client import make_wsgi_app, Counter, Histogram, Gauge
from werkzeug.middleware.dispatcher import DispatcherMiddleware

os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/inventory-service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

otlp_endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://tempo:4317')
service_name = os.getenv('OTEL_SERVICE_NAME', 'inventory-service')

resource = Resource.create({
    "service.name": service_name,
    "service.version": "1.0.0",
})

trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

try:
    otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
    span_processor = BatchSpanProcessor(otlp_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
    logger.info(f"OTLP exporter configured: {otlp_endpoint}")
except Exception as e:
    logger.warning(f"Failed to setup OTLP exporter: {e}")

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

http_requests_total = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status', 'service'])
http_request_duration_seconds = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint', 'service'])
active_requests = Gauge('active_requests', 'Active HTTP requests', ['service'])

@app.before_request
def before_request():
    request.start_time = time.time()
    active_requests.labels(service='inventory-service').inc()

@app.after_request
def after_request(response):
    duration = time.time() - request.start_time
    http_request_duration_seconds.labels(method=request.method, endpoint=request.endpoint or 'unknown', service='inventory-service').observe(duration)
    http_requests_total.labels(method=request.method, endpoint=request.endpoint or 'unknown', status=response.status_code, service='inventory-service').inc()
    active_requests.labels(service='inventory-service').dec()
    return response

@app.route('/')
def home():
    with tracer.start_as_current_span("inventory_service_home") as span:
        span.set_attribute("service.name", "inventory-service")
        return jsonify({"service": "inventory-service", "message": "Inventory Management Service"})

@app.route('/health')
def health():
    with tracer.start_as_current_span("inventory_service_health") as span:
        span.set_attribute("service.name", "inventory-service")
        return jsonify({"status": "healthy", "service": "inventory-service"})

@app.route('/inventory')
def get_inventory():
    with tracer.start_as_current_span("get_inventory") as span:
        span.set_attribute("service.name", "inventory-service")
        time.sleep(random.uniform(0.1, 0.4))
        items = [
            {"id": 1, "name": "Product A", "quantity": 100},
            {"id": 2, "name": "Product B", "quantity": 50},
        ]
        logger.info(f"Retrieved {len(items)} inventory items")
        return jsonify({"items": items})

@app.route('/inventory/<int:item_id>')
def get_item(item_id):
    with tracer.start_as_current_span("get_item") as span:
        span.set_attribute("service.name", "inventory-service")
        span.set_attribute("item.id", item_id)
        time.sleep(random.uniform(0.1, 0.3))
        item = {"id": item_id, "name": f"Product {item_id}", "quantity": random.randint(10, 200)}
        logger.info(f"Retrieved item {item_id}")
        return jsonify({"item": item})

@app.route('/inventory/<int:item_id>/reserve', methods=['POST'])
def reserve_item(item_id):
    with tracer.start_as_current_span("reserve_item") as span:
        span.set_attribute("service.name", "inventory-service")
        span.set_attribute("item.id", item_id)
        
        data = request.get_json() or {}
        quantity = data.get('quantity', 1)
        
        time.sleep(random.uniform(0.2, 0.5))
        
        # Call shipping service
        shipping_service_url = os.getenv('SHIPPING_SERVICE_URL', 'http://shipping-service:8004')
        try:
            logger.info(f"Calling shipping service for item {item_id}")
            requests.get(f"{shipping_service_url}/shipping/check", timeout=5)
        except Exception as e:
            logger.warning(f"Failed to call shipping service: {e}")
        
        result = {"item_id": item_id, "quantity": quantity, "status": "reserved"}
        logger.info(f"Reserved {quantity} units of item {item_id}")
        return jsonify({"reservation": result}), 201

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {'/metrics': make_wsgi_app()})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8003))
    app.run(host='0.0.0.0', port=port, debug=False)

