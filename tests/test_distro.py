import platform

from opentelemetry.metrics import get_meter_provider
from opentelemetry.trace import get_tracer_provider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter as HTTPSpanExporter
)
from tgt.opentelemetry.distro import configure_opentelemetry
from tgt.opentelemetry.options import TgtOptions
from tgt.opentelemetry.version import __version__


def test_distro_configure_defaults():
    configure_opentelemetry()
    tracer_provider = get_tracer_provider()
    assert tracer_provider._resource._attributes["service.name"] == "unknown_service:python"
    assert tracer_provider._resource._attributes["tgt.distro.version"] == __version__
    assert tracer_provider._resource._attributes["tgt.distro.runtime_version"] == platform.python_version(
    )

    active_span_processors = tracer_provider._active_span_processor._span_processors
    assert len(active_span_processors) == 1
    (batch) = active_span_processors
    assert isinstance(batch, BatchSpanProcessor)
    assert isinstance(batch.span_exporter, HTTPSpanExporter)

    meter_provider = get_meter_provider()
    # a real meter provider has it's _sdk_config property set, ensure we have a reader configured
    assert len(meter_provider._sdk_config.metric_readers) == 1

def test_can_disable_metrics():
    # metrics is enabled by providing a metrics dataset
    options = TgtOptions(metrics_disabled="True")
    configure_opentelemetry(options)

    meter_provider = get_meter_provider()
    # the noop meter provider does not have the _sdk_config property where meter readers are configured
    assert not hasattr(meter_provider, "_sdk_config")
