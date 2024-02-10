import logging
import os
from opentelemetry.sdk.environment_variables import (
    OTEL_EXPORTER_OTLP_ENDPOINT,
    OTEL_EXPORTER_OTLP_INSECURE,
    OTEL_EXPORTER_OTLP_METRICS_PROTOCOL,
    OTEL_EXPORTER_OTLP_METRICS_INSECURE,
    OTEL_EXPORTER_OTLP_METRICS_ENDPOINT,
    OTEL_EXPORTER_OTLP_PROTOCOL,
    OTEL_EXPORTER_OTLP_TRACES_ENDPOINT,
    OTEL_EXPORTER_OTLP_TRACES_INSECURE,
    OTEL_EXPORTER_OTLP_TRACES_PROTOCOL,
    OTEL_LOG_LEVEL,
    OTEL_SERVICE_NAME
)

OTEL_SERVICE_VERSION = "OTEL_SERVICE_VERSION"
DEBUG = "DEBUG"
CLOUD_APPLICATION = "CLOUD_APPLICATION"
METRICS_DISABLED = "METRICS_DISABLED"
TRACES_DISABLED = "TRACES_DISABLED"


# Deployment environements
TAP_DEPLOYMENT = "TAP"
STORES_DEPLOYMENT = "STORES"
UNKNOWN_DEPLOYMENT = "UNKNOWN"

# Default values
DEFAULT_EXPORTER_OTLP_ENDPOINT = "telemetry.prod.target.com"
DEFAULT_EXPORTER_PROTOCOL = "http/protobuf"
DEFAULT_SERVICE_NAME = "unknown_service:python"
DEFAULT_LOG_LEVEL = "ERROR"
DEFAULT_DEPLOYMENT = UNKNOWN_DEPLOYMENT

# Errors and Warnings
INVALID_DEBUG_ERROR = "Unable to parse DEBUG environment variable. " + \
    "Defaulting to False."
INVALID_METRICS_DISABLED_ERROR = "Unable to parse " + \
    "METRICS_DISABLED. Defaulting to False."
INVALID_TRACES_DISABLED_ERROR = "Unable to parse " + \
    "TRACES_DISABLED. Defaulting to False."
INVALID_EXPORTER_PROTOCOL_ERROR = "Invalid OTLP exporter protocol " + \
    "detected. Must be one of ['http/protobuf']. Defaulting to http/protobuf."
INVALID_INSECURE_ERROR = "Unable to parse " + \
    "OTEL_EXPORTER_OTLP_INSECURE. Defaulting to False."
INVALID_METRICS_INSECURE_ERROR = "Unable to parse " + \
    "OTEL_EXPORTER_OTLP_METRICS_INSECURE. Defaulting to False."
INVALID_TRACES_INSECURE_ERROR = "Unable to parse " + \
    "OTEL_EXPORTER_OTLP_TRACES_INSECURE. Defaulting to False."
MISSING_SERVICE_NAME_ERROR = "Missing service name. Specify either " + \
    "OTEL_SERVICE_NAME environment variable or service_name in the " + \
    "options parameter. If left unset, this will show up in UI " + \
    "as unknown_service:python"
# not currently supported in OTel SDK, open PR:
# https://github.com/open-telemetry/opentelemetry-specification/issues/1901

log_levels = {
    "NOTSET": logging.NOTSET,
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

EXPORTER_PROTOCOL_HTTP_PROTO = "http/protobuf"

TRACES_HTTP_PATH = "v1/traces"
METRICS_HTTP_PATH = "v1/metrics"

exporter_protocols = {
    EXPORTER_PROTOCOL_HTTP_PROTO
}

_logger = logging.getLogger(__name__)

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

def parse_bool(environment_variable: str,
               default_value: bool,
               error_message: str,
               deployment: str) -> bool:
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

def get_default_insecure(deployment: str) -> bool:
    """
    Attempts to determine if insecure should default to true or false based on deployment.
    """
    if deployment == TAP_DEPLOYMENT:
        return True
    return False


def detect_environment() -> str:
    """
    Attempts to detect environment based on environment variables, starting with container,
    moving to SITE_NAME.
    """
    if os.environ.get("container", None):
        return TAP_DEPLOYMENT
    elif os.environ.get("SITE_NAME", None):
        return STORES_DEPLOYMENT
    else:
        return UNKNOWN_DEPLOYMENT

# pylint: disable=too-many-arguments,too-many-instance-attributes
class TgtOptions:
    """
    Target Options used to configure the OpenTelemetry SDK.

    Setting the debug flag TRUE enables verbose logging and sets the
    OTEL_LOG_LEVEL to DEBUG.

    An option set as an environment variable will override any existing
    options declared as parameter variables, if neither are present it
    will fall back to the default value.

    Defaults are declared at the top of this file, i.e. DEFAULT_EXPORTER_OTLP_ENDPOINT = telemetry.prod.target.com
    """
    service_name = DEFAULT_SERVICE_NAME
    service_version = None
    traces_endpoint = DEFAULT_EXPORTER_OTLP_ENDPOINT
    metrics_endpoint = DEFAULT_EXPORTER_OTLP_ENDPOINT
    traces_endpoint_insecure = False
    metrics_endpoint_insecure = False
    traces_exporter_protocol = DEFAULT_EXPORTER_PROTOCOL
    metrics_exporter_protocol = DEFAULT_EXPORTER_PROTOCOL
    debug = False
    deployment = DEFAULT_DEPLOYMENT
    metrics_disabled = False
    traces_disabled = False

    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    def __init__(
        self,
        service_name: str = None,
        service_version: str = None,
        traces_endpoint: str = None,
        metrics_endpoint: str = None,
        endpoint_insecure: bool = False,
        traces_endpoint_insecure: bool = False,
        metrics_endpoint_insecure: bool = False,
        log_level: str = None,
        exporter_protocol: str = EXPORTER_PROTOCOL_HTTP_PROTO,
        traces_exporter_protocol: str = None,
        metrics_exporter_protocol: str = None,
        debug: bool = False,
        deployment: str = DEFAULT_DEPLOYMENT,
        metrics_disabled: bool = False,
        traces_disabled: bool = False
    ):
        # Detect deployment

        self.deployment = detect_environment()
        if self.deployment == TAP_DEPLOYMENT:
            DEFAULT_EXPORTER_OTLP_ENDPOINT = "127.0.0.1:4318"
        elif self.deployment == STORES_DEPLOYMENT:
            DEFAULT_EXPORTER_OTLP_ENDPOINT = "telemetry.storeapi.target.com"

        self.metrics_disabled = parse_bool(
            METRICS_DISABLED,
            (metrics_disabled or False),
            INVALID_METRICS_DISABLED_ERROR
        )

        self.traces_disabled = parse_bool(
            TRACES_DISABLED,
            (traces_disabled or False),
            INVALID_TRACES_DISABLED_ERROR
        )

        self.debug = parse_bool(
            DEBUG,
            (debug or False),
            INVALID_DEBUG_ERROR
        )
        if self.debug:
            self.log_level = "DEBUG"
        else:
            log_level = os.environ.get(OTEL_LOG_LEVEL, log_level)
            if log_level and log_level.upper() in log_levels:
                self.log_level = log_level.upper()

        logging.basicConfig(level=log_levels[self.log_level])

        self.service_name = os.environ.get(OTEL_SERVICE_NAME, service_name)
        if not self.service_name:
            _logger.warning(MISSING_SERVICE_NAME_ERROR)
            self.service_name = os.environ.get(
                CLOUD_APPLICATION, DEFAULT_SERVICE_NAME
            )

        if not self.service_name:
            _logger.warning(MISSING_SERVICE_NAME_ERROR)
            self.service_name = os.environ.get(
                CLOUD_APPLICATION, DEFAULT_SERVICE_NAME
            )

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
                        DEFAULT_EXPORTER_OTLP_ENDPOINT
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
                        DEFAULT_EXPORTER_OTLP_ENDPOINT
                    )

        endpoint_insecure = parse_bool(
            OTEL_EXPORTER_OTLP_INSECURE,
            (endpoint_insecure or get_default_insecure(deployment)),
            INVALID_INSECURE_ERROR,
            deployment
        )
        self.traces_endpoint_insecure = parse_bool(
            OTEL_EXPORTER_OTLP_TRACES_INSECURE,
            (traces_endpoint_insecure or endpoint_insecure),
            INVALID_TRACES_INSECURE_ERROR
        )
        self.metrics_endpoint_insecure = parse_bool(
            OTEL_EXPORTER_OTLP_METRICS_INSECURE,
            (metrics_endpoint_insecure or endpoint_insecure),
            INVALID_METRICS_INSECURE_ERROR
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
