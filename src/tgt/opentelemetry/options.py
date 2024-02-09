import logging
import os
from opentelemetry.sdk.environment_variables import (
    OTEL_EXPORTER_OTLP_ENDPOINT,
    OTEL_EXPORTER_OTLP_METRICS_ENDPOINT,
    OTEL_EXPORTER_OTLP_METRICS_PROTOCOL,
    OTEL_EXPORTER_OTLP_PROTOCOL,
    OTEL_EXPORTER_OTLP_TRACES_ENDPOINT,
    OTEL_EXPORTER_OTLP_TRACES_PROTOCOL,
    OTEL_LOG_LEVEL,
    OTEL_SERVICE_NAME
)

# Default values
DEFAULT_EXPORTER_PROTOCOL = "http/protobuf"
DEFAULT_SERVICE_NAME = "unknown_service:python"

# Errors and Warnings
INVALID_EXPORTER_PROTOCOL_ERROR = "Invalid OTLP exporter protocol " + \
    "detected. Must be one of ['http/protobuf']. Defaulting to http/protobuf."
MISSING_SERVICE_NAME_ERROR = "Missing service name. Specify either " + \
    "OTEL_SERVICE_NAME environment variable or service_name in the " + \
    "options parameter. If left unset, this will show up in UI " + \
    "as unknown_service:python"
# not currently supported in OTel SDK, open PR:
# https://github.com/open-telemetry/opentelemetry-specification/issues/1901

EXPORTER_PROTOCOL_HTTP_PROTO = "http/protobuf"

TRACES_HTTP_PATH = "v1/traces"
METRICS_HTTP_PATH = "v1/metrics"

exporter_protocols = {
    EXPORTER_PROTOCOL_HTTP_PROTO
}

_logger = logging.getLogger(__name__)

def parse_bool(environment_variable: str,
               default_value: bool,
               error_message: str) -> bool:
    """
    Attempts to parse the provided environment variable into a bool. If it
    does not exist or fails parse, the default value is returned instead.

    Args:
        environment_variable (str): the environment variable name to use
        default_value (bool): the default value if not found or unable parse
        error_message (str): the error message to log if unable to parse

    Returns:
        bool: either the parsed environment variable or default value
    """
    val = os.getenv(environment_variable, None)
    if val:
        try:
            return bool(val)
        except ValueError:
            _logger.warning(error_message)
    return default_value


def parse_int(environment_variable: str,
              param: int,
              default_value: int,
              error_message: str) -> int:
    """
    Attempts to parse the provided environment variable into an int. If it
    does not exist or fails parse, the default value is returned instead.

    Args:
        environment_variable (str): the environment variable name to use
        param(int): fallback parameter to check before setting default
        default_value (int): the default value if not found or unable parse
        error_message (str): the error message to log if unable to parse

    Returns:
        int: either the parsed environment variable, param, or default value
    """
    val = os.getenv(environment_variable, None)
    if val:
        try:
            return int(val)
        except ValueError:
            _logger.warning(error_message)
            return default_value
    elif isinstance(param, int):
        return param
    else:
        return default_value


def _append_traces_path(protocol: str, endpoint: str) -> str:
    """
    Appends the OTLP traces HTTP path '/v1/traces' to the endpoint if the
    protocol is http/protobuf and it doesn't already exist.

    Returns:
        string: the endpoint, optionally appended with traces path
    """
    if endpoint and protocol == "http/protobuf" \
       and not endpoint.strip("/").endswith(TRACES_HTTP_PATH):
        return "/".join([endpoint.strip("/"), TRACES_HTTP_PATH])
    return endpoint


def _append_metrics_path(protocol: str, endpoint: str) -> str:
    """
    Appends the OTLP metrics HTTP path '/v1/metrics' to the endpoint if the
    protocol is http/protobuf and it doesn't already exist.

    Returns:
        string: the endpoint, optionally appended with metrics path
    """
    if endpoint and protocol == "http/protobuf" \
       and not endpoint.strip("/").endswith(METRICS_HTTP_PATH):
        return "/".join([endpoint.strip("/"), METRICS_HTTP_PATH])
    return endpoint


# pylint: disable=too-many-arguments,too-many-instance-attributes
class TgtOptions:
    """
    Target Options used to configure the OpenTelemetry SDK.

    Setting the debug flag TRUE enables verbose logging and sets the
    OTEL_LOG_LEVEL to DEBUG.

    An option set as an environment variable will override any existing
    options declared as parameter variables, if neither are present it
    will fall back to the default value.

    Defaults are declared at the top of this file, i.e. DEFAULT_SAMPLE_RATE = 1
    """
    service_name = DEFAULT_SERVICE_NAME
    service_version = None
    traces_endpoint = None
    metrics_endpoint = None
    traces_endpoint_insecure = False
    metrics_endpoint_insecure = False
    traces_exporter_protocol = DEFAULT_EXPORTER_PROTOCOL
    metrics_exporter_protocol = DEFAULT_EXPORTER_PROTOCOL
    debug = False
    dataset = None
    metrics_dataset = None

    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    def __init__(
        self,
        service_name: str = None,
        service_version: str = None,
        traces_endpoint: str = None,
        metrics_endpoint: str = None,
        debug: bool = False,
        log_level: str = None,
        exporter_protocol: str = EXPORTER_PROTOCOL_HTTP_PROTO,
        traces_exporter_protocol: str = None,
        metrics_exporter_protocol: str = None
    ):
        log_level = os.environ.get(OTEL_LOG_LEVEL, log_level)
        if log_level and log_level.upper() in log_levels:
                self.log_level = log_level.upper()
        logging.basicConfig(level=log_levels[self.log_level])

        self.service_name = os.environ.get(OTEL_SERVICE_NAME, service_name)
        if not self.service_name:
            _logger.warning(MISSING_SERVICE_NAME_ERROR)
            self.service_name = DEFAULT_SERVICE_NAME
        self.service_version = os.environ.get(
            OTEL_SERVICE_VERSION, service_version)

        exporter_protocol = os.environ.get(
            OTEL_EXPORTER_OTLP_PROTOCOL,
            (exporter_protocol or DEFAULT_EXPORTER_PROTOCOL))
        if exporter_protocol not in exporter_protocols:
            _logger.warning(INVALID_EXPORTER_PROTOCOL_ERROR)
            exporter_protocol = DEFAULT_EXPORTER_PROTOCOL

        self.traces_exporter_protocol = os.environ.get(
            OTEL_EXPORTER_OTLP_TRACES_PROTOCOL,
            (traces_exporter_protocol or exporter_protocol))
        if traces_exporter_protocol and (
                traces_exporter_protocol not in exporter_protocols):
            _logger.warning(INVALID_EXPORTER_PROTOCOL_ERROR)
            self.traces_exporter_protocol = exporter_protocol

        self.metrics_exporter_protocol = os.environ.get(
            OTEL_EXPORTER_OTLP_METRICS_PROTOCOL,
            (metrics_exporter_protocol or exporter_protocol))
        if metrics_exporter_protocol and (
                metrics_exporter_protocol not in exporter_protocols):
            _logger.warning(INVALID_EXPORTER_PROTOCOL_ERROR)
            self.metrics_exporter_protocol = exporter_protocol

        self.traces_endpoint = os.environ.get(
            OTEL_EXPORTER_OTLP_TRACES_ENDPOINT,
            None
        )
        if not self.traces_endpoint:
            self.traces_endpoint = _append_traces_path(
                self.traces_exporter_protocol,
                os.environ.get(OTEL_EXPORTER_OTLP_ENDPOINT, None)
            )
            if not self.traces_endpoint:
                self.traces_endpoint = traces_endpoint
                if not self.traces_endpoint:
                    self.traces_endpoint = _append_traces_path(
                        self.traces_exporter_protocol,
                        self.endpoint
                    )

        # if http/protobuf protocol and using generic env or param
        # append /v1/metrics path
        self.metrics_endpoint = os.environ.get(
            OTEL_EXPORTER_OTLP_METRICS_ENDPOINT,
            None
        )
        if not self.metrics_endpoint:
            self.metrics_endpoint = _append_metrics_path(
                self.metrics_exporter_protocol,
                os.environ.get(OTEL_EXPORTER_OTLP_ENDPOINT, None)
            )
            if not self.metrics_endpoint:
                self.metrics_endpoint = metrics_endpoint
                if not self.metrics_endpoint:
                    self.metrics_endpoint = _append_metrics_path(
                        self.metrics_exporter_protocol,
                        self.endpoint
                    )

    def get_traces_endpoint(self) -> str:
        """
        Returns the OTLP traces endpoint to send spans to.
        """
        return self.traces_endpoint

    def get_metrics_endpoint(self) -> str:
        """
        Returns the OTLP metrics endpoint to send metrics to.
        """
        return self.metrics_endpoint
