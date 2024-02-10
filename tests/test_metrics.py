from opentelemetry.sdk.metrics import MeterProvider

from tgt.opentelemetry.options import TgtOptions
from tgt.opentelemetry.resource import create_resource
from tgt.opentelemetry.metrics import create_meter_provider


def test_returns_meter_provider():
    options = TgtOptions()
    resource = create_resource(options)
    meter_provider = create_meter_provider(options, resource)
    assert isinstance(meter_provider, MeterProvider)
    assert len(meter_provider._sdk_config.metric_readers) == 1


def test_setting_debug_adds_console_exporter():
    options = TgtOptions(debug=True)
    resource = create_resource(options)
    meter_provider = create_meter_provider(options, resource)
    assert isinstance(meter_provider, MeterProvider)
    assert len(meter_provider._sdk_config.metric_readers) == 1
