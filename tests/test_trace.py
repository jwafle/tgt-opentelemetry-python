from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SimpleSpanProcessor
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter as HTTPSpanExporter
)
from tgt.opentelemetry.options import TgtOptions
from tgt.opentelemetry.resource import create_resource
from tgt.opentelemetry.trace import create_tracer_provider

"""
Tracer Provider only provides one of two span processors.

BatchSpanProcessor (HTTP Exporter)
SimpleSpanProcessor (Console Exporter)

"""


def test_returns_tracer_provider_with_batch_and_baggage_span_processors():
    options = TgtOptions()
    resource = create_resource(options)
    tracer_provider = create_tracer_provider(options, resource)

    active_span_processors = tracer_provider._active_span_processor._span_processors
    assert len(active_span_processors) == 2
    assert any(
        isinstance(span_processor, BatchSpanProcessor)
        for span_processor in active_span_processors
        )


def test_http_protocol_configures_http_span_exporter_on_batch_span_processor():
    options = TgtOptions(traces_exporter_protocol="http/protobuf")
    resource = create_resource(options)
    tracer_provider = create_tracer_provider(options, resource)

    active_span_processors = tracer_provider._active_span_processor._span_processors
    assert len(active_span_processors) == 2
    (baggage, batch) = active_span_processors
    assert isinstance(batch, BatchSpanProcessor)
    assert isinstance(batch.span_exporter, HTTPSpanExporter)


def test_setting_debug_adds_console_exporter_on_simple_span_processor():
    options = TgtOptions(debug=True)
    resource = create_resource(options)
    tracer_provider = create_tracer_provider(options, resource)

    active_span_processors = tracer_provider._active_span_processor._span_processors
    assert len(active_span_processors) == 1

    (console) = active_span_processors
    assert isinstance(console, SimpleSpanProcessor)
    assert isinstance(console.span_exporter, ConsoleSpanExporter)

def test_setting_no_flags_enables_all_batch_span_processors():
    options = TgtOptions()
    resource = create_resource(options)
    tracer_provider = create_tracer_provider(options, resource)

    active_span_processors = tracer_provider._active_span_processor._span_processors
    assert len(active_span_processors) == 1

    (batch) = active_span_processors
    assert isinstance(batch, BatchSpanProcessor)
    assert isinstance(batch.span_exporter, HTTPSpanExporter)
