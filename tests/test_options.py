from opentelemetry.sdk.environment_variables import (
    OTEL_EXPORTER_OTLP_ENDPOINT,
    OTEL_EXPORTER_OTLP_METRICS_ENDPOINT,
    OTEL_EXPORTER_OTLP_TRACES_ENDPOINT,
    OTEL_SERVICE_NAME,
)
from tgt.opentelemetry.options import (
    EXPORTER_PROTOCOL_HTTP_PROTO,
    TgtOptions,
)

EXPECTED_ENDPOINT = "expected endpoint"


def test_defaults():
    options = TgtOptions()
    assert options.traces_apikey is None
    assert options.metrics_apikey is None
    assert options.service_name == "unknown_service:python"
    assert options.traces_exporter_protocol is EXPORTER_PROTOCOL_HTTP_PROTO
    assert options.metrics_exporter_protocol is EXPORTER_PROTOCOL_HTTP_PROTO


def test_can_set_service_name_with_param():
    options = TgtOptions(service_name="my-service")
    assert options.service_name == "my-service"


def test_can_set_service_name_with_envvar(monkeypatch):
    monkeypatch.setenv(OTEL_SERVICE_NAME, "my-service")
    options = TgtOptions()
    assert options.service_name == "my-service"


def test_can_set_generic_api_endpoint_with_param():
    options = TgtOptions(endpoint=EXPECTED_ENDPOINT)
    assert options.get_traces_endpoint() == EXPECTED_ENDPOINT
    assert options.get_metrics_endpoint() == EXPECTED_ENDPOINT


def test_can_set_traces_endpoint_with_param():
    options = TgtOptions(traces_endpoint=EXPECTED_ENDPOINT)
    assert options.get_traces_endpoint() == EXPECTED_ENDPOINT


def test_can_set_traces_endpoint_with_traces_envvar(monkeypatch):
    monkeypatch.setenv(OTEL_EXPORTER_OTLP_TRACES_ENDPOINT, EXPECTED_ENDPOINT)
    options = TgtOptions()
    assert options.get_traces_endpoint() == EXPECTED_ENDPOINT


def test_can_set_traces_endpoint_with_endpoint_envvar(monkeypatch):
    monkeypatch.setenv(OTEL_EXPORTER_OTLP_ENDPOINT, EXPECTED_ENDPOINT)
    options = TgtOptions()
    assert options.get_traces_endpoint() == EXPECTED_ENDPOINT


def test_traces_endpoint_set_from_generic_env_beats_params(monkeypatch):
    monkeypatch.setenv(OTEL_EXPORTER_OTLP_ENDPOINT, EXPECTED_ENDPOINT)
    options = TgtOptions(
        endpoint="generic param",
        traces_endpoint="specific param"
    )
    assert options.get_traces_endpoint() == EXPECTED_ENDPOINT


def test_traces_endpoint_specific_env_beats_params(monkeypatch):
    monkeypatch.setenv(OTEL_EXPORTER_OTLP_TRACES_ENDPOINT, EXPECTED_ENDPOINT)
    options = TgtOptions(
        endpoint="generic param",
        traces_endpoint="specific param"
    )
    assert options.get_traces_endpoint() == EXPECTED_ENDPOINT


def test_traces_endpoint_set_from_specific_param_beats_generic_param():
    options = TgtOptions(
        endpoint="generic param",
        traces_endpoint=EXPECTED_ENDPOINT
    )
    assert options.get_traces_endpoint() == EXPECTED_ENDPOINT


def test_traces_endpoint_set_from_traces_env_beats_params(
        monkeypatch):
    monkeypatch.setenv(OTEL_EXPORTER_OTLP_ENDPOINT, "generic env")
    monkeypatch.setenv(OTEL_EXPORTER_OTLP_TRACES_ENDPOINT, EXPECTED_ENDPOINT)
    options = TgtOptions(
        endpoint="generic param",
        traces_endpoint="specific param"
    )
    assert options.get_traces_endpoint() == EXPECTED_ENDPOINT


def test_can_set_metrics_endpoint_with_param():
    options = TgtOptions(metrics_endpoint=EXPECTED_ENDPOINT)
    assert options.get_metrics_endpoint() == EXPECTED_ENDPOINT


def test_can_set_metrics_endpoint_with_metrics_envvar(monkeypatch):
    monkeypatch.setenv(OTEL_EXPORTER_OTLP_METRICS_ENDPOINT, EXPECTED_ENDPOINT)
    options = TgtOptions()
    assert options.get_metrics_endpoint() == EXPECTED_ENDPOINT


def test_can_set_metrics_endpoint_with_endpoint_envvar(monkeypatch):
    monkeypatch.setenv(OTEL_EXPORTER_OTLP_ENDPOINT, EXPECTED_ENDPOINT)
    options = TgtOptions()
    assert options.get_metrics_endpoint() == EXPECTED_ENDPOINT


def test_get_traces_endpoint_returns_endpoint_when_traces_endpoint_not_set():
    options = TgtOptions(endpoint=EXPECTED_ENDPOINT)
    assert options.get_traces_endpoint() == EXPECTED_ENDPOINT


def test_get_metrics_endpoint_returns_endpoint_when_metrics_endpoint_not_set():
    options = TgtOptions(endpoint=EXPECTED_ENDPOINT)
    assert options.get_metrics_endpoint() == EXPECTED_ENDPOINT


def test_metrics_endpoint_set_from_generic_env_beats_params(monkeypatch):
    monkeypatch.setenv(OTEL_EXPORTER_OTLP_ENDPOINT, EXPECTED_ENDPOINT)
    options = TgtOptions(
        endpoint="generic param",
        metrics_endpoint="specific param"
    )
    assert options.get_metrics_endpoint() == EXPECTED_ENDPOINT


def test_metrics_endpoint_specific_env_beats_params(monkeypatch):
    monkeypatch.setenv(OTEL_EXPORTER_OTLP_METRICS_ENDPOINT, EXPECTED_ENDPOINT)
    options = TgtOptions(
        endpoint="generic param",
        metrics_endpoint="specific param"
    )
    assert options.get_metrics_endpoint() == EXPECTED_ENDPOINT


def test_metrics_endpoint_set_from_specific_param_beats_generic_param():
    options = TgtOptions(
        endpoint="generic param",
        metrics_endpoint=EXPECTED_ENDPOINT
    )
    assert options.get_metrics_endpoint() == EXPECTED_ENDPOINT


def test_metrics_endpoint_set_from_metrics_env_beats_params(
        monkeypatch):
    monkeypatch.setenv(OTEL_EXPORTER_OTLP_ENDPOINT, "generic env")
    monkeypatch.setenv(OTEL_EXPORTER_OTLP_METRICS_ENDPOINT, EXPECTED_ENDPOINT)
    options = TgtOptions(
        endpoint="generic param",
        metrics_endpoint="specific param"
    )
    assert options.get_metrics_endpoint() == EXPECTED_ENDPOINT

def test_get_traces_endpoint_with_http_proto_protocol_returns_correctly_formatted_endpoint(monkeypatch):
    # http
    protocol = EXPORTER_PROTOCOL_HTTP_PROTO

    # default endpoint
    options = TgtOptions(exporter_protocol=protocol)
    assert options.get_traces_endpoint() == DEFAULT_API_ENDPOINT + "/v1/traces"

    # generic endpoint param
    options = TgtOptions(
        exporter_protocol=protocol, endpoint=EXPECTED_ENDPOINT)
    assert options.get_traces_endpoint() == EXPECTED_ENDPOINT + "/v1/traces"

    # traces endpoint param
    options = TgtOptions(
        exporter_protocol=protocol, traces_endpoint=EXPECTED_ENDPOINT)
    assert options.get_traces_endpoint() == EXPECTED_ENDPOINT

    # generic endpoint env
    monkeypatch.setenv(OTEL_EXPORTER_OTLP_ENDPOINT, EXPECTED_ENDPOINT)
    options = TgtOptions(exporter_protocol=protocol)
    assert options.get_traces_endpoint() == EXPECTED_ENDPOINT + "/v1/traces"

    # traces endpoint env
    monkeypatch.setenv(OTEL_EXPORTER_OTLP_TRACES_ENDPOINT, EXPECTED_ENDPOINT)
    options = TgtOptions(exporter_protocol=protocol)
    assert options.get_traces_endpoint() == EXPECTED_ENDPOINT

def test_get_traces_endpoint_with_traces_path_and_http_proto_returns_corretly_formatted_endpoint(monkeypatch):
    # http
    protocol = EXPORTER_PROTOCOL_HTTP_PROTO

    # endpoint already has /v1/traces
    endpoint = DEFAULT_API_ENDPOINT + "/v1/traces"

    # set endpoint in options
    options = TgtOptions(exporter_protocol=protocol, endpoint=endpoint)
    assert options.get_traces_endpoint() == endpoint

def test_get_metrics_endpoint_with_http_proto_protocol_returns_correctly_formatted_endpoint(monkeypatch):
    # http
    protocol = EXPORTER_PROTOCOL_HTTP_PROTO

    # default endpoint
    options = TgtOptions(exporter_protocol=protocol)
    assert options.get_metrics_endpoint() == DEFAULT_API_ENDPOINT + "/v1/metrics"

    # generic endpoint param
    options = TgtOptions(
        exporter_protocol=protocol, endpoint=EXPECTED_ENDPOINT)
    assert options.get_metrics_endpoint() == EXPECTED_ENDPOINT + "/v1/metrics"

    # metrics endpoint param
    options = TgtOptions(
        exporter_protocol=protocol, metrics_endpoint=EXPECTED_ENDPOINT)
    assert options.get_metrics_endpoint() == EXPECTED_ENDPOINT

    # generic endpoint env
    monkeypatch.setenv(OTEL_EXPORTER_OTLP_ENDPOINT, EXPECTED_ENDPOINT)
    options = TgtOptions(exporter_protocol=protocol)
    assert options.get_metrics_endpoint() == EXPECTED_ENDPOINT + "/v1/metrics"

    # metrics endpoint env
    monkeypatch.setenv(OTEL_EXPORTER_OTLP_METRICS_ENDPOINT, EXPECTED_ENDPOINT)
    options = TgtOptions(exporter_protocol=protocol)
    assert options.get_metrics_endpoint() == EXPECTED_ENDPOINT

def test_get_metrics_endpoint_with_metrics_path_and_http_proto_returns_corretly_formatted_endpoint(monkeypatch):
    # http
    protocol = EXPORTER_PROTOCOL_HTTP_PROTO

    # endpoint already has /v1/metrics
    endpoint = DEFAULT_API_ENDPOINT + "/v1/metrics"

    # set endpoint in options
    options = TgtOptions(exporter_protocol=protocol, endpoint=endpoint)
    assert options.get_metrics_endpoint() == endpoint
