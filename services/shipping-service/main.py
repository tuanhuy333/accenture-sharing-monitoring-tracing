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
        logging.FileHandler('logs/shipping-service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

otlp_endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://tempo:4317')
service_name = os.getenv('OTEL_SERVICE_NAME', 'shipping-service')

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
    active_requests.labels(service='shipping-service').inc()

@app.after_request
def after_request(response):
    duration = time.time() - request.start_time
    http_request_duration_seconds.labels(method=request.method, endpoint=request.endpoint or 'unknown', service='shipping-service').observe(duration)
    http_requests_total.labels(method=request.method, endpoint=request.endpoint or 'unknown', status=response.status_code, service='shipping-service').inc()
    active_requests.labels(service='shipping-service').dec()
    return response

@app.route('/')
def home():
    with tracer.start_as_current_span("shipping_service_home") as span:
        span.set_attribute("service.name", "shipping-service")
        return jsonify({"service": "shipping-service", "message": "Shipping Management Service"})

@app.route('/health')
def health():
    with tracer.start_as_current_span("shipping_service_health") as span:
        span.set_attribute("service.name", "shipping-service")
        return jsonify({"status": "healthy", "service": "shipping-service"})

@app.route('/shipping/check')
def check_shipping():
    with tracer.start_as_current_span("check_shipping") as span:
        span.set_attribute("service.name", "shipping-service")
        time.sleep(random.uniform(0.2, 0.6))
        
        # Call notification service
        notification_service_url = os.getenv('NOTIFICATION_SERVICE_URL', 'http://notification-service:8005')
        try:
            logger.info("Calling notification service")
            requests.post(f"{notification_service_url}/notifications", json={"type": "shipping_check"}, timeout=5)
        except Exception as e:
            logger.warning(f"Failed to call notification service: {e}")
        
        return jsonify({"available": True, "estimated_days": random.randint(1, 5)})

@app.route('/shipping')
def get_shippings():
    with tracer.start_as_current_span("get_shippings") as span:
        span.set_attribute("service.name", "shipping-service")
        time.sleep(random.uniform(0.1, 0.4))
        shippings = [
            {"id": 1, "order_id": 1, "status": "in_transit", "tracking": "TRACK001"},
            {"id": 2, "order_id": 2, "status": "delivered", "tracking": "TRACK002"},
        ]
        return jsonify({"shippings": shippings})

@app.route('/shipping/<int:shipping_id>')
def get_shipping(shipping_id):
    with tracer.start_as_current_span("get_shipping") as span:
        span.set_attribute("service.name", "shipping-service")
        span.set_attribute("shipping.id", shipping_id)
        time.sleep(random.uniform(0.1, 0.3))
        shipping = {"id": shipping_id, "order_id": random.randint(1, 10), "status": random.choice(["pending", "in_transit", "delivered"])}
        return jsonify({"shipping": shipping})

@app.route('/shipping', methods=['POST'])
def create_shipping():
    with tracer.start_as_current_span("create_shipping") as span:
        span.set_attribute("service.name", "shipping-service")
        data = request.get_json() or {}
        order_id = data.get('order_id')
        
        if not order_id:
            return jsonify({"error": "order_id is required"}), 400
        
        span.set_attribute("order.id", order_id)
        time.sleep(random.uniform(0.3, 0.7))
        
        shipping = {"id": random.randint(100, 999), "order_id": order_id, "status": "pending", "tracking": f"TRACK{random.randint(1000, 9999)}"}
        logger.info(f"Created shipping for order {order_id}")
        return jsonify({"shipping": shipping}), 201

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {'/metrics': make_wsgi_app()})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8004))
    app.run(host='0.0.0.0', port=port, debug=False)

