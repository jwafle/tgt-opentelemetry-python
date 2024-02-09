import platform
from tgt.opentelemetry.options import TgtOptions
from tgt.opentelemetry.resource import create_resource
from tgt.opentelemetry.version import __version__


def test_default_resource():
    options = TgtOptions()
    resource = create_resource(options)
    assert resource._attributes["service.name"] == "unknown_service:python"
    assert "service.version" not in resource._attributes
    assert resource._attributes["tgt.distro.version"] == __version__
    assert resource._attributes["tgt.distro.runtime_version"] == platform.python_version(
    )


def test_can_set_service_name():
    options = TgtOptions(service_name="my-service")
    resource = create_resource(options)
    assert resource._attributes["service.name"] == "my-service"
    assert resource._attributes["tgt.distro.version"] == __version__
    assert resource._attributes["tgt.distro.runtime_version"] == platform.python_version(
    )


def test_can_set_service_version():
    options = TgtOptions(service_version="1.2.3")
    resource = create_resource(options)
    assert resource._attributes["service.version"] == "1.2.3"
