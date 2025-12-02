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

# Setup logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/user-service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Setup OpenTelemetry
otlp_endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://tempo:4317')
service_name = os.getenv('OTEL_SERVICE_NAME', 'user-service')

resource = Resource.create({
    "service.name": service_name,
    "service.version": "1.0.0",
})

trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

try:
    otlp_exporter = OTLPSpanExporter(
        endpoint=otlp_endpoint,
        insecure=True
    )
    span_processor = BatchSpanProcessor(otlp_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
    logger.info(f"OTLP exporter configured: {otlp_endpoint}")
except Exception as e:
    logger.warning(f"Failed to setup OTLP exporter: {e}")

# Create Flask app
app = Flask(__name__)

# Instrument Flask and Requests
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

# Prometheus metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status', 'service']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint', 'service']
)

active_requests = Gauge(
    'active_requests',
    'Active HTTP requests',
    ['service']
)

@app.before_request
def before_request():
    request.start_time = time.time()
    active_requests.labels(service='user-service').inc()

@app.after_request
def after_request(response):
    duration = time.time() - request.start_time
    http_request_duration_seconds.labels(
        method=request.method,
        endpoint=request.endpoint or 'unknown',
        service='user-service'
    ).observe(duration)
    
    http_requests_total.labels(
        method=request.method,
        endpoint=request.endpoint or 'unknown',
        status=response.status_code,
        service='user-service'
    ).inc()
    
    active_requests.labels(service='user-service').dec()
    return response

@app.route('/')
def home():
    with tracer.start_as_current_span("user_service_home") as span:
        span.set_attribute("http.method", "GET")
        span.set_attribute("http.route", "/")
        span.set_attribute("service.name", "user-service")
        
        logger.info("User service home endpoint accessed")
        return jsonify({
            "service": "user-service",
            "message": "User Management Service",
            "endpoints": ["/", "/health", "/users", "/users/<id>"]
        })

@app.route('/health')
def health():
    with tracer.start_as_current_span("user_service_health") as span:
        span.set_attribute("service.name", "user-service")
        logger.info("User service health check")
        return jsonify({"status": "healthy", "service": "user-service"})

@app.route('/users')
def get_users():
    with tracer.start_as_current_span("get_users") as span:
        span.set_attribute("service.name", "user-service")
        
        # Simulate database query
        time.sleep(random.uniform(0.1, 0.5))
        
        users = [
            {"id": 1, "name": "John Doe", "email": "john@example.com"},
            {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
        ]
        
        logger.info(f"Retrieved {len(users)} users")
        span.set_attribute("users.count", len(users))
        
        return jsonify({"users": users})

@app.route('/users/<int:user_id>')
def get_user(user_id):
    with tracer.start_as_current_span("get_user") as span:
        span.set_attribute("service.name", "user-service")
        span.set_attribute("user.id", user_id)
        
        # Simulate database query
        time.sleep(random.uniform(0.1, 0.3))
        
        user = {"id": user_id, "name": f"User {user_id}", "email": f"user{user_id}@example.com"}
        
        logger.info(f"Retrieved user {user_id}")
        
        return jsonify({"user": user})

@app.route('/users/<int:user_id>/orders')
def get_user_orders(user_id):
    with tracer.start_as_current_span("get_user_orders") as span:
        span.set_attribute("service.name", "user-service")
        span.set_attribute("user.id", user_id)
        
        # Call order service
        order_service_url = os.getenv('ORDER_SERVICE_URL', 'http://order-service:8001')
        
        try:
            logger.info(f"Calling order service for user {user_id}")
            response = requests.get(f"{order_service_url}/orders?user_id={user_id}", timeout=5)
            orders = response.json() if response.status_code == 200 else []
            span.set_attribute("orders.count", len(orders.get('orders', [])))
            return jsonify({"user_id": user_id, "orders": orders.get('orders', [])})
        except Exception as e:
            logger.error(f"Failed to call order service: {e}")
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
            return jsonify({"error": "Failed to fetch orders"}), 500

# Add Prometheus metrics endpoint
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)

