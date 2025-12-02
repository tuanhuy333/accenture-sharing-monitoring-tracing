import os
import time
import random
import logging
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
        logging.FileHandler('logs/notification-service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

otlp_endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://tempo:4317')
service_name = os.getenv('OTEL_SERVICE_NAME', 'notification-service')

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
notifications_sent = Counter('notifications_sent_total', 'Total notifications sent', ['service', 'type'])

@app.before_request
def before_request():
    request.start_time = time.time()
    active_requests.labels(service='notification-service').inc()

@app.after_request
def after_request(response):
    duration = time.time() - request.start_time
    http_request_duration_seconds.labels(method=request.method, endpoint=request.endpoint or 'unknown', service='notification-service').observe(duration)
    http_requests_total.labels(method=request.method, endpoint=request.endpoint or 'unknown', status=response.status_code, service='notification-service').inc()
    active_requests.labels(service='notification-service').dec()
    return response

@app.route('/')
def home():
    with tracer.start_as_current_span("notification_service_home") as span:
        span.set_attribute("service.name", "notification-service")
        return jsonify({"service": "notification-service", "message": "Notification Service"})

@app.route('/health')
def health():
    with tracer.start_as_current_span("notification_service_health") as span:
        span.set_attribute("service.name", "notification-service")
        return jsonify({"status": "healthy", "service": "notification-service"})

@app.route('/notifications')
def get_notifications():
    with tracer.start_as_current_span("get_notifications") as span:
        span.set_attribute("service.name", "notification-service")
        time.sleep(random.uniform(0.1, 0.3))
        notifications = [
            {"id": 1, "type": "order_confirmed", "message": "Your order has been confirmed"},
            {"id": 2, "type": "shipping_update", "message": "Your order has shipped"},
        ]
        return jsonify({"notifications": notifications})

@app.route('/notifications', methods=['POST'])
def send_notification():
    with tracer.start_as_current_span("send_notification") as span:
        span.set_attribute("service.name", "notification-service")
        data = request.get_json() or {}
        notification_type = data.get('type', 'generic')
        
        span.set_attribute("notification.type", notification_type)
        time.sleep(random.uniform(0.2, 0.8))
        
        notifications_sent.labels(service='notification-service', type=notification_type).inc()
        
        notification = {"id": random.randint(1000, 9999), "type": notification_type, "status": "sent", "sent_at": time.time()}
        logger.info(f"Sent notification: {notification_type}")
        return jsonify({"notification": notification}), 201

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {'/metrics': make_wsgi_app()})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8005))
    app.run(host='0.0.0.0', port=port, debug=False)

