from opentelemetry import context
from opentelemetry.trace import SpanKind
from opentelemetry.sdk.trace.sampling import (
    ParentBased,
    DEFAULT_OFF,
    Decision
)

from tgt.opentelemetry.options import (
    TgtOptions,
)
from tgt.opentelemetry.sampler import (
    configure_sampler,
    DeterministicSampler
)


def get_sampling_result(test_sampler):
    return test_sampler.should_sample(
        context.get_current(),  # parent_context
        112345678999,  # trace id
        "the_best_span",  # span name
        SpanKind.CLIENT,
        {"existing_attr": "is intact"},
        [],  # links
        {}  # trace state
    )


def test_sample_with_undefined_rate_defaults_to_ALWAYS_ON_and_recorded():
    default_off_sampler = configure_sampler()
    # test the inner sampler choice
    inner_sampler = default_off_sampler._sampler
    assert inner_sampler == DEFAULT_OFF
    assert isinstance(default_off_sampler, ParentBased)
    # test the SamplingResult is as expected
    sampling_result = get_sampling_result(undefined_rate_sampler)
    assert sampling_result.decision.is_sampled()
    assert sampling_result.attributes == {
        'existing_attr': 'is intact',
    }


def test_sampler_with_rate_of_zero_is_ALWAYS_OFF_and_DROP():
    sample_rate_zero = TgtOptions(sample_rate=0)
    always_off_sampler = configure_sampler(sample_rate_zero)
    # test the inner DeterministicSampler choice and rate
    inner_sampler = always_off_sampler._sampler
    assert inner_sampler == ALWAYS_OFF
    assert isinstance(always_off_sampler, DeterministicSampler)
    assert always_off_sampler.rate == 0
    # test the SamplingResult is as expected
    sampling_result = get_sampling_result(always_off_sampler)
    assert sampling_result.decision.is_sampled() is False
    assert sampling_result.decision == Decision.DROP
    assert sampling_result.attributes == {}
