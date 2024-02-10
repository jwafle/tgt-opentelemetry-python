import platform
import os
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from tgt.opentelemetry.options import TgtOptions, TAP_DEPLOYMENT
from tgt.opentelemetry.version import __version__

HOSTNAME = "HOSTNAME"
CLOUD_ENVIRONMENT = "CLOUD_ENVIRONMENT"
CLOUD_REGION = "CLOUD_REGION"
CONTAINER = "container"
CONTAINER_IMAGE = "container_image"
CLOUD_SERVER_GROUP = "CLOUD_SERVER_GROUP"
CLOUD_CLUSTER = "CLOUD_CLUSTER"
CLOUD_STACK = "CLOUD_STACK"
CLOUD_DETAIL = "CLOUD_DETAIL"

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
        ResourceAttributes.SERVICE_NAME: options.service_name,
        ResourceAttributes.SCOPE_NAME: "tgt-opentelemetry-python",
        ResourceAttributes.SCOPE_VERSION: __version__,
        ResourceAttributes.PROCESS_RUNTIME_NAME: "python",

        "tgt.distro.runtime_version": platform.python_version()
    }
    if options.service_version:
        attributes[ResourceAttributes.SERVICE_VERSION] = options.service_version

    deploymentEnvironment = os.environ.get(CLOUD_ENVIRONMENT, None)
    if deploymentEnvironment:
        attributes[ResourceAttributes.DEPLOYMENT_ENVIRONMENT] = deploymentEnvironment

    cloudRegion = os.environ.get(CLOUD_REGION, None)
    if cloudRegion:
        attributes[ResourceAttributes.CLOUD_REGION] = cloudRegion

    containerName = os.environ.get(CONTAINER, None)
    if containerName:
        attributes[ResourceAttributes.CONTAINER_NAME] = containerName

    containerImageName = os.environ.get(CONTAINER, None)
    if containerImageName:
        attributes[ResourceAttributes.CONTAINER_IMAGE_NAME] = containerImageName

    hostName = os.environ.get(HOSTNAME, None)
    if hostName:
        attributes["host.name"] = hostName

    serverGroup = os.environ.get(CLOUD_SERVER_GROUP, None)
    if serverGroup:
        attributes["labels.server_group"] = serverGroup

    cluster = os.environ.get(CLOUD_CLUSTER, None)
    if cluster:
        attributes["labels.cluster"] = cluster

    stack = os.environ.get(CLOUD_STACK, None)
    if stack:
        attributes["labels.stack"] = stack

    detail = os.environ.get(CLOUD_DETAIL, None)
    if detail:
        attributes["labels.detail"] = detail

    return Resource.create(attributes)
