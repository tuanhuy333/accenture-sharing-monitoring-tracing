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
        logging.FileHandler('logs/order-service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Setup OpenTelemetry
otlp_endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://tempo:4317')
service_name = os.getenv('OTEL_SERVICE_NAME', 'order-service')

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
    active_requests.labels(service='order-service').inc()

@app.after_request
def after_request(response):
    duration = time.time() - request.start_time
    http_request_duration_seconds.labels(
        method=request.method,
        endpoint=request.endpoint or 'unknown',
        service='order-service'
    ).observe(duration)
    
    http_requests_total.labels(
        method=request.method,
        endpoint=request.endpoint or 'unknown',
        status=response.status_code,
        service='order-service'
    ).inc()
    
    active_requests.labels(service='order-service').dec()
    return response

@app.route('/')
def home():
    with tracer.start_as_current_span("order_service_home") as span:
        span.set_attribute("service.name", "order-service")
        logger.info("Order service home endpoint accessed")
        return jsonify({
            "service": "order-service",
            "message": "Order Management Service",
            "endpoints": ["/", "/health", "/orders", "/orders/<id>"]
        })

@app.route('/health')
def health():
    with tracer.start_as_current_span("order_service_health") as span:
        span.set_attribute("service.name", "order-service")
        logger.info("Order service health check")
        return jsonify({"status": "healthy", "service": "order-service"})

@app.route('/orders')
def get_orders():
    with tracer.start_as_current_span("get_orders") as span:
        span.set_attribute("service.name", "order-service")
        
        user_id = request.args.get('user_id', type=int)
        if user_id:
            span.set_attribute("user.id", user_id)
        
        # Simulate database query
        time.sleep(random.uniform(0.2, 0.8))
        
        orders = [
            {"id": 1, "user_id": 1, "total": 99.99, "status": "completed"},
            {"id": 2, "user_id": 1, "total": 149.99, "status": "pending"},
            {"id": 3, "user_id": 2, "total": 79.99, "status": "completed"},
        ]
        
        if user_id:
            orders = [o for o in orders if o['user_id'] == user_id]
        
        logger.info(f"Retrieved {len(orders)} orders")
        span.set_attribute("orders.count", len(orders))
        
        return jsonify({"orders": orders})

@app.route('/orders/<int:order_id>')
def get_order(order_id):
    with tracer.start_as_current_span("get_order") as span:
        span.set_attribute("service.name", "order-service")
        span.set_attribute("order.id", order_id)
        
        # Simulate database query
        time.sleep(random.uniform(0.1, 0.4))
        
        order = {
            "id": order_id,
            "user_id": random.randint(1, 2),
            "total": round(random.uniform(50, 200), 2),
            "status": random.choice(["pending", "completed", "cancelled"])
        }
        
        logger.info(f"Retrieved order {order_id}")
        
        # Call payment service to get payment info
        payment_service_url = os.getenv('PAYMENT_SERVICE_URL', 'http://payment-service:8002')
        
        try:
            logger.info(f"Calling payment service for order {order_id}")
            payment_response = requests.get(f"{payment_service_url}/payments?order_id={order_id}", timeout=5)
            if payment_response.status_code == 200:
                payment_data = payment_response.json()
                order['payment'] = payment_data.get('payments', [{}])[0] if payment_data.get('payments') else {}
        except Exception as e:
            logger.warning(f"Failed to call payment service: {e}")
        
        return jsonify({"order": order})

@app.route('/orders', methods=['POST'])
def create_order():
    with tracer.start_as_current_span("create_order") as span:
        span.set_attribute("service.name", "order-service")
        
        # Get trace ID
        current_span = trace.get_current_span()
        trace_id = format(current_span.get_span_context().trace_id, '032x') if current_span else None
        
        data = request.get_json() or {}
        user_id = data.get('user_id')
        inject_error = data.get('inject_error', False)
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        span.set_attribute("user.id", user_id)
        if trace_id:
            span.set_attribute("trace.id", trace_id)
        
        # Call inventory service to check availability
        inventory_service_url = os.getenv('INVENTORY_SERVICE_URL', 'http://inventory-service:8003')
        try:
            logger.info(f"Checking inventory for order - Trace ID: {trace_id}")
            requests.get(f"{inventory_service_url}/inventory/1", timeout=5)
        except Exception as e:
            logger.warning(f"Failed to call inventory service: {e}")
        
        # Simulate order creation
        time.sleep(random.uniform(0.3, 0.6))
        
        order = {
            "id": random.randint(100, 999),
            "user_id": user_id,
            "total": data.get('total', round(random.uniform(50, 200), 2)),
            "status": "pending",
            "trace_id": trace_id
        }
        
        logger.info(f"Created order {order['id']} for user {user_id} - Trace ID: {trace_id}")
        
        # Call payment service to process payment
        payment_service_url = os.getenv('PAYMENT_SERVICE_URL', 'http://payment-service:8002')
        try:
            logger.info(f"Processing payment for order {order['id']} - Trace ID: {trace_id}")
            payment_response = requests.post(
                f"{payment_service_url}/payments",
                json={
                    "order_id": order['id'],
                    "amount": order['total'],
                    "method": "credit_card",
                    "inject_error": inject_error
                },
                timeout=10
            )
            
            if payment_response.status_code == 201:
                payment_data = payment_response.json()
                order['payment'] = payment_data.get('payment', {})
                order['payment_trace_id'] = payment_data.get('trace_id')
                logger.info(f"Payment processed successfully - Trace ID: {payment_data.get('trace_id')}")
            else:
                payment_data = payment_response.json()
                order['payment_error'] = payment_data.get('error', 'Payment failed')
                order['payment_trace_id'] = payment_data.get('trace_id')
                logger.error(f"Payment failed - Trace ID: {payment_data.get('trace_id')}")
                span.set_status(trace.Status(trace.StatusCode.ERROR, f"Payment failed: {order['payment_error']}"))
                return jsonify({
                    "order": order,
                    "error": "Order created but payment failed",
                    "trace_id": trace_id
                }), 500
        except Exception as e:
            logger.error(f"Failed to call payment service: {e}")
            span.set_status(trace.Status(trace.StatusCode.ERROR, f"Payment service call failed: {str(e)}"))
        
        return jsonify({"order": order, "trace_id": trace_id}), 201

# Add Prometheus metrics endpoint
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8001))
    app.run(host='0.0.0.0', port=port, debug=False)

