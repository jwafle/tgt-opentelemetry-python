import os
from opentelemetry import trace, baggage, metrics
from opentelemetry.context import attach, detach
from tgt.opentelemetry import configure_opentelemetry, TgtOptions

configure_opentelemetry(
    TgtOptions(
        debug=True,  # prints exported traces & metrics to the console, useful for debugging and setting up
        service_name="otel-python-example",
        # service_version = None, Set a version for this service, will show up as an attribute on all spans
        exporter_protocol=os.getenv("OTEL_EXPORTER_OTLP_PROTOCOL", "http/protobuf"),
        # traces_exporter_protocol = "grpc", Set a specific exporter protocol just for traces, grpc or http/protobuf
        # metrics_exporter_protocol = "grpc", Set a specific exporter protocol just for metrics, grpc or http/protobuf
        # sample_rate = DEFAULT_SAMPLE_RATE, Set a sample rate for spans
        # Set a metrics dataset to enable metrics
    )
)

meter = metrics.get_meter("hello_world_meter")
sheep = meter.create_counter('sheep')

tracer = trace.get_tracer("hello_world_tracer")


def hello_world():
    token = attach(baggage.set_baggage(
        "baggy", "important_value"))
    with tracer.start_as_current_span(name="hello"):
        token_second = attach(baggage.set_baggage(
            "for_the_children", "another_important_value"))
        with tracer.start_as_current_span(name="world") as span:
            span.set_attribute("message", "hello world!")
            print("Hello World")
        detach(token_second)
    detach(token)
    sheep.add(1, {'app.route': '/'})
    return "Hello World"


hello_world()
