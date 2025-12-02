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
        logging.FileHandler('logs/auth-service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

otlp_endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://tempo:4317')
service_name = os.getenv('OTEL_SERVICE_NAME', 'auth-service')

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
    active_requests.labels(service='auth-service').inc()

@app.after_request
def after_request(response):
    duration = time.time() - request.start_time
    http_request_duration_seconds.labels(method=request.method, endpoint=request.endpoint or 'unknown', service='auth-service').observe(duration)
    http_requests_total.labels(method=request.method, endpoint=request.endpoint or 'unknown', status=response.status_code, service='auth-service').inc()
    active_requests.labels(service='auth-service').dec()
    return response

@app.route('/')
def home():
    with tracer.start_as_current_span("auth_service_home") as span:
        span.set_attribute("service.name", "auth-service")
        return jsonify({"service": "auth-service", "message": "Authentication Service"})

@app.route('/health')
def health():
    with tracer.start_as_current_span("auth_service_health") as span:
        span.set_attribute("service.name", "auth-service")
        return jsonify({"status": "healthy", "service": "auth-service"})

@app.route('/auth/login', methods=['POST'])
def login():
    with tracer.start_as_current_span("login") as span:
        span.set_attribute("service.name", "auth-service")
        data = request.get_json() or {}
        username = data.get('username')
        
        if not username:
            return jsonify({"error": "username is required"}), 400
        
        span.set_attribute("user.username", username)
        time.sleep(random.uniform(0.3, 0.8))
        
        # Call user service to verify
        user_service_url = os.getenv('USER_SERVICE_URL', 'http://user-service:8000')
        try:
            logger.info(f"Verifying user {username}")
            requests.get(f"{user_service_url}/users/1", timeout=5)
        except Exception as e:
            logger.warning(f"Failed to call user service: {e}")
        
        token = f"token_{random.randint(10000, 99999)}"
        logger.info(f"User {username} logged in")
        return jsonify({"token": token, "user": username})

@app.route('/auth/verify')
def verify_token():
    with tracer.start_as_current_span("verify_token") as span:
        span.set_attribute("service.name", "auth-service")
        token = request.args.get('token')
        
        if not token:
            return jsonify({"error": "token is required"}), 400
        
        span.set_attribute("token.prefix", token[:10] if len(token) > 10 else token)
        time.sleep(random.uniform(0.1, 0.3))
        
        is_valid = token.startswith('token_')
        return jsonify({"valid": is_valid, "user_id": random.randint(1, 10) if is_valid else None})

@app.route('/auth/users/<int:user_id>/permissions')
def get_permissions(user_id):
    with tracer.start_as_current_span("get_permissions") as span:
        span.set_attribute("service.name", "auth-service")
        span.set_attribute("user.id", user_id)
        time.sleep(random.uniform(0.1, 0.4))
        permissions = ["read", "write", "delete"]
        return jsonify({"user_id": user_id, "permissions": permissions})

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {'/metrics': make_wsgi_app()})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8007))
    app.run(host='0.0.0.0', port=port, debug=False)

