from logging import getLogger
from typing import Optional

from opentelemetry.sdk.trace.sampling import (
    DEFAULT_OFF,
    Sampler,
    SamplingResult
)

from opentelemetry.trace import Link, SpanKind
from opentelemetry.trace.span import TraceState
from opentelemetry.util.types import Attributes
from opentelemetry.context import Context

from tgt.opentelemetry.options import (
    TgtOptions
)

_logger = getLogger(__name__)


def configure_sampler(
    options: Optional[TgtOptions] = None,
):
    """Configures and returns an OpenTelemetry Sampler that is
    configured based on the sample_rate determined in HoneycombOptions.
    The configuration initializes a DeterministicSampler with
    an inner sampler of either AlwaysOn (1), AlwaysOff (0),
    or a TraceIdRatio as 1/N.

    These samplers do not take into account the parent span's
    sampling decision.

    Args:
        options (HoneycombOptions): the HoneycombOptions containing
        sample_rate used to configure the deterministic sampler.

    Returns:
        DeterministicSampler: the configured Sampler based on sample_rate
    """
    return DEFAULT_OFF
