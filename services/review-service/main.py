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
        logging.FileHandler('logs/review-service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

otlp_endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://tempo:4317')
service_name = os.getenv('OTEL_SERVICE_NAME', 'review-service')

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
    active_requests.labels(service='review-service').inc()

@app.after_request
def after_request(response):
    duration = time.time() - request.start_time
    http_request_duration_seconds.labels(method=request.method, endpoint=request.endpoint or 'unknown', service='review-service').observe(duration)
    http_requests_total.labels(method=request.method, endpoint=request.endpoint or 'unknown', status=response.status_code, service='review-service').inc()
    active_requests.labels(service='review-service').dec()
    return response

@app.route('/')
def home():
    with tracer.start_as_current_span("review_service_home") as span:
        span.set_attribute("service.name", "review-service")
        return jsonify({"service": "review-service", "message": "Review Service"})

@app.route('/health')
def health():
    with tracer.start_as_current_span("review_service_health") as span:
        span.set_attribute("service.name", "review-service")
        return jsonify({"status": "healthy", "service": "review-service"})

@app.route('/reviews')
def get_reviews():
    with tracer.start_as_current_span("get_reviews") as span:
        span.set_attribute("service.name", "review-service")
        product_id = request.args.get('product_id', type=int)
        
        if product_id:
            span.set_attribute("product.id", product_id)
        
        time.sleep(random.uniform(0.1, 0.4))
        reviews = [
            {"id": 1, "product_id": 1, "rating": 5, "comment": "Great product!"},
            {"id": 2, "product_id": 1, "rating": 4, "comment": "Good value"},
            {"id": 3, "product_id": 2, "rating": 5, "comment": "Excellent!"},
        ]
        
        if product_id:
            reviews = [r for r in reviews if r['product_id'] == product_id]
        
        logger.info(f"Retrieved {len(reviews)} reviews")
        return jsonify({"reviews": reviews})

@app.route('/reviews/<int:review_id>')
def get_review(review_id):
    with tracer.start_as_current_span("get_review") as span:
        span.set_attribute("service.name", "review-service")
        span.set_attribute("review.id", review_id)
        time.sleep(random.uniform(0.1, 0.3))
        review = {"id": review_id, "product_id": random.randint(1, 10), "rating": random.randint(1, 5), "comment": f"Review {review_id}"}
        return jsonify({"review": review})

@app.route('/reviews', methods=['POST'])
def create_review():
    with tracer.start_as_current_span("create_review") as span:
        span.set_attribute("service.name", "review-service")
        data = request.get_json() or {}
        product_id = data.get('product_id')
        
        if not product_id:
            return jsonify({"error": "product_id is required"}), 400
        
        span.set_attribute("product.id", product_id)
        time.sleep(random.uniform(0.2, 0.5))
        
        # Call notification service
        notification_service_url = os.getenv('NOTIFICATION_SERVICE_URL', 'http://notification-service:8005')
        try:
            logger.info(f"Calling notification service for review")
            requests.post(f"{notification_service_url}/notifications", json={"type": "review_created"}, timeout=5)
        except Exception as e:
            logger.warning(f"Failed to call notification service: {e}")
        
        review = {"id": random.randint(100, 999), "product_id": product_id, "rating": data.get('rating', random.randint(1, 5)), "comment": data.get('comment', '')}
        logger.info(f"Created review for product {product_id}")
        return jsonify({"review": review}), 201

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {'/metrics': make_wsgi_app()})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8006))
    app.run(host='0.0.0.0', port=port, debug=False)

