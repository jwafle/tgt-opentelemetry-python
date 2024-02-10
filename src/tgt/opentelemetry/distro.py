"""This honey-flavored Distro configures OpenTelemetry for use with Honeycomb.

Typical usage example:

    using the opentelemetry-instrument command with
    requisite env variables set:

    $bash> opentelemetry-instrument python program.py

    or configured by code within your service:
    configure_opentelemetry(
        TgtOptions(
            service_name="tgt-python-example"
        )
    )
"""
from logging import getLogger
from typing import Optional
from opentelemetry.instrumentation.distro import BaseDistro
from opentelemetry.metrics import set_meter_provider
from opentelemetry.trace import set_tracer_provider
from tgt.opentelemetry.metrics import create_meter_provider
from tgt.opentelemetry.options import TgtOptions
from tgt.opentelemetry.resource import create_resource
from tgt.opentelemetry.trace import create_tracer_provider

_logger = getLogger(__name__)


def configure_opentelemetry(
    options: Optional[TgtOptions] = None,
):
    """
    Configures the OpenTelemetry SDK to send telemetry to Honeycomb.

    Args:
        options (HoneycombOptions, optional): the HoneycombOptions used to
        configure the the SDK. These options can be set either as parameters
        to this function or through environment variables

        Note: API key is a required option.
    """
    if options is None:
        options = TgtOptions()
    _logger.info("🎯 Configuring OpenTelemetry using Target distro 🎯")
    _logger.debug(vars(options))
    resource = create_resource(options)
    if not options.traces_disabled:
        set_tracer_provider(
            create_tracer_provider(options, resource)
        )
        _logger.info("started traces")
    else:
        _logger.info("traces disabled via TRACES_DISABLED environment variable")
    if not options.metrics_disabled:
        set_meter_provider(
            create_meter_provider(options, resource)
        )
        _logger.info("started metrics")
    else:
        _logger.info("metrics disabled via METRICS_DISABLED environment variable")



# pylint: disable=too-few-public-methods
class TargetDistro(BaseDistro):
    """
    An extension of the base python OpenTelemetry distro, which provides
    a mechanism to automatically configure some of the more common options
    for users. This class is auto-detected by the `opentelemetry-instrument`
    command.

    This class doesn't need to be touched directly when using the distro. If
    you'd like to explicitly set configuration in code, use the
    configure_opentelemetry() function above instead of the
    `opentelemetry-instrument` command.

    If you're wondering about the under-the-hood magic - we add the following
    declaration to package metadata in our pyproject.toml, like so:

    [tool.poetry.plugins."opentelemetry_distro"]
    distro = "tgt.opentelemetry.distro:TargetDistro"
    """

    def _configure(self, **kwargs):
        configure_opentelemetry()
