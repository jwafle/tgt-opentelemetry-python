from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    PeriodicExportingMetricReader,
    ConsoleMetricExporter
)
from opentelemetry.exporter.otlp.proto.http.metric_exporter import (
    OTLPMetricExporter as HTTPMetricExporter
)
from tgt.opentelemetry.options import TgtOptions


def create_meter_provider(options: TgtOptions, resource: Resource):
    """
    Configures and returns a new MeterProvider to send metrics telemetry.

    Args:
        options (HoneycombOptions): the Honeycomb options to configure with
        resource (Resource): the resource to use with the new meter provider

    Returns:
        MeterProvider: the new meter provider
    """
    exporter = HTTPMetricExporter(
        endpoint=options.get_metrics_endpoint(),
        headers=options.get_metrics_headers()
    )
    readers = []
    if options.debug:
        readers.append(
            PeriodicExportingMetricReader(
                ConsoleMetricExporter(),
            )
        )
    else:
        readers.append(
            PeriodicExportingMetricReader(
                exporter
            )
        )

    return MeterProvider(
        metric_readers=readers,
        resource=resource
    )
