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
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Setup OpenTelemetry
otlp_endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://tempo:4317')
service_name = os.getenv('OTEL_SERVICE_NAME', 'demo-app')

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
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

active_requests = Gauge(
    'active_requests',
    'Active HTTP requests'
)

@app.before_request
def before_request():
    request.start_time = time.time()
    active_requests.inc()

@app.after_request
def after_request(response):
    duration = time.time() - request.start_time
    http_request_duration_seconds.labels(
        method=request.method,
        endpoint=request.endpoint or 'unknown'
    ).observe(duration)
    
    http_requests_total.labels(
        method=request.method,
        endpoint=request.endpoint or 'unknown',
        status=response.status_code
    ).inc()
    
    active_requests.dec()
    return response

@app.route('/')
def home():
    with tracer.start_as_current_span("home_handler") as span:
        span.set_attribute("http.method", "GET")
        span.set_attribute("http.route", "/")
        
        logger.info("Home endpoint accessed")
        return jsonify({
            "message": "Demo App with OTLP Auto-Instrumentation",
            "endpoints": [
                "/",
                "/health",
                "/slow",
                "/error",
                "/random"
            ]
        })

@app.route('/health')
def health():
    with tracer.start_as_current_span("health_check") as span:
        span.set_attribute("http.method", "GET")
        span.set_attribute("http.route", "/health")
        
        logger.info("Health check performed")
        return jsonify({"status": "healthy"})

@app.route('/slow')
def slow():
    with tracer.start_as_current_span("slow_handler") as span:
        span.set_attribute("http.method", "GET")
        span.set_attribute("http.route", "/slow")
        
        delay = random.uniform(1, 3)
        logger.warning(f"Slow endpoint called, delaying {delay:.2f}s")
        
        time.sleep(delay)
        
        span.set_attribute("delay_seconds", delay)
        return jsonify({"message": f"Slow response after {delay:.2f}s"})

@app.route('/error')
def error():
    with tracer.start_as_current_span("error_handler") as span:
        span.set_attribute("http.method", "GET")
        span.set_attribute("http.route", "/error")
        span.set_status(trace.Status(trace.StatusCode.ERROR, "Intentional error"))
        
        error_rate = random.random()
        logger.error(f"Error endpoint called, error_rate: {error_rate:.2f}")
        
        if error_rate > 0.3:
            return jsonify({"error": "Internal Server Error"}), 500
        else:
            return jsonify({"message": "No error this time"})

@app.route('/random')
def random_endpoint():
    with tracer.start_as_current_span("random_handler") as span:
        span.set_attribute("http.method", "GET")
        span.set_attribute("http.route", "/random")
        
        result = random.choice(['success', 'warning', 'info'])
        logger.info(f"Random endpoint returned: {result}")
        
        span.set_attribute("result", result)
        
        if result == 'warning':
            logger.warning("Random warning generated")
        
        return jsonify({"result": result})

# Add Prometheus metrics endpoint
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

if __name__ == '__main__':
    import os
    os.makedirs('logs', exist_ok=True)
    app.run(host='0.0.0.0', port=8000, debug=False)

