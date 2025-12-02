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

# Setup logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/payment-service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Setup OpenTelemetry
otlp_endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://tempo:4317')
service_name = os.getenv('OTEL_SERVICE_NAME', 'payment-service')

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

payment_processing_time = Histogram(
    'payment_processing_seconds',
    'Payment processing time',
    ['service', 'status']
)

@app.before_request
def before_request():
    request.start_time = time.time()
    active_requests.labels(service='payment-service').inc()

@app.after_request
def after_request(response):
    duration = time.time() - request.start_time
    http_request_duration_seconds.labels(
        method=request.method,
        endpoint=request.endpoint or 'unknown',
        service='payment-service'
    ).observe(duration)
    
    http_requests_total.labels(
        method=request.method,
        endpoint=request.endpoint or 'unknown',
        status=response.status_code,
        service='payment-service'
    ).inc()
    
    active_requests.labels(service='payment-service').dec()
    return response

@app.route('/')
def home():
    with tracer.start_as_current_span("payment_service_home") as span:
        span.set_attribute("service.name", "payment-service")
        logger.info("Payment service home endpoint accessed")
        return jsonify({
            "service": "payment-service",
            "message": "Payment Processing Service",
            "endpoints": ["/", "/health", "/payments", "/payments/<id>", "/payments", "POST"]
        })

@app.route('/health')
def health():
    with tracer.start_as_current_span("payment_service_health") as span:
        span.set_attribute("service.name", "payment-service")
        logger.info("Payment service health check")
        return jsonify({"status": "healthy", "service": "payment-service"})

@app.route('/payments')
def get_payments():
    with tracer.start_as_current_span("get_payments") as span:
        span.set_attribute("service.name", "payment-service")
        
        order_id = request.args.get('order_id', type=int)
        if order_id:
            span.set_attribute("order.id", order_id)
        
        # Simulate database query
        time.sleep(random.uniform(0.1, 0.5))
        
        payments = [
            {"id": 1, "order_id": 1, "amount": 99.99, "status": "completed", "method": "credit_card"},
            {"id": 2, "order_id": 2, "amount": 149.99, "status": "pending", "method": "paypal"},
            {"id": 3, "order_id": 3, "amount": 79.99, "status": "completed", "method": "credit_card"},
        ]
        
        if order_id:
            payments = [p for p in payments if p['order_id'] == order_id]
        
        logger.info(f"Retrieved {len(payments)} payments")
        span.set_attribute("payments.count", len(payments))
        
        return jsonify({"payments": payments})

@app.route('/payments/<int:payment_id>')
def get_payment(payment_id):
    with tracer.start_as_current_span("get_payment") as span:
        span.set_attribute("service.name", "payment-service")
        span.set_attribute("payment.id", payment_id)
        
        # Simulate database query
        time.sleep(random.uniform(0.1, 0.3))
        
        payment = {
            "id": payment_id,
            "order_id": random.randint(1, 10),
            "amount": round(random.uniform(50, 200), 2),
            "status": random.choice(["pending", "completed", "failed"]),
            "method": random.choice(["credit_card", "paypal", "bank_transfer"])
        }
        
        logger.info(f"Retrieved payment {payment_id}")
        
        return jsonify({"payment": payment})

@app.route('/payments', methods=['POST'])
def process_payment():
    with tracer.start_as_current_span("process_payment") as span:
        span.set_attribute("service.name", "payment-service")
        
        data = request.get_json() or {}
        order_id = data.get('order_id')
        amount = data.get('amount')
        
        if not order_id or not amount:
            return jsonify({"error": "order_id and amount are required"}), 400
        
        span.set_attribute("order.id", order_id)
        span.set_attribute("payment.amount", amount)
        
        # Simulate payment processing (sometimes slow, sometimes fails)
        processing_start = time.time()
        processing_time = random.uniform(0.5, 2.0)
        time.sleep(processing_time)
        
        # 10% chance of failure
        success = random.random() > 0.1
        
        payment = {
            "id": random.randint(1000, 9999),
            "order_id": order_id,
            "amount": amount,
            "status": "completed" if success else "failed",
            "method": data.get('method', 'credit_card'),
            "processed_at": time.time()
        }
        
        payment_processing_time.labels(
            service='payment-service',
            status=payment['status']
        ).observe(processing_time)
        
        if success:
            logger.info(f"Payment processed successfully for order {order_id}")
        else:
            logger.error(f"Payment failed for order {order_id}")
            span.set_status(trace.Status(trace.StatusCode.ERROR, "Payment processing failed"))
            return jsonify({"error": "Payment processing failed", "payment": payment}), 500
        
        return jsonify({"payment": payment}), 201

# Add Prometheus metrics endpoint
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8002))
    app.run(host='0.0.0.0', port=port, debug=False)

