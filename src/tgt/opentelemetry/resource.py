import platform
from opentelemetry.sdk.resources import Resource
from tgt.opentelemetry.options import TgtOptions
from tgt.opentelemetry.version import __version__


def create_resource(options: TgtOptions):
    """
    Configures and returns a new OpenTelemetry Resource.

    Args:
        options (TgtOptions): the Honeycomb options to configure with
        resource (Resource): the resource to use with the new resource

    Returns:
        MeterProvider: the new Resource
    """
    attributes = {
        "service.name": options.service_name,
        "tgt.distro.version": __version__,
        "tgt.distro.runtime_version": platform.python_version()
    }
    if options.service_version:
        attributes["service.version"] = options.service_version
    return Resource.create(attributes)
