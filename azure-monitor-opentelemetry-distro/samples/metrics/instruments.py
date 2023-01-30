# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from typing import Iterable

from opentelemetry import metrics
from opentelemetry.metrics import CallbackOptions, Observation

from azure.monitor.opentelemetry.distro import configure_azure_monitor

# Configure Azure monitor collection telemetry pipeline
configure_azure_monitor(
    connection_string="<your-connection-string>",
    service_name="metric_instrument_service",
    disable_logging=True,
    disable_tracing=True,
    metrics_export_interval_millis=30000,
)

# Create a namespaced meter
meter = metrics.get_meter_provider().get_meter("sample")

# Callback functions for observable instruments
def observable_counter_func(options: CallbackOptions) -> Iterable[Observation]:
    yield Observation(1, {})


def observable_up_down_counter_func(
    options: CallbackOptions,
) -> Iterable[Observation]:
    yield Observation(-10, {})


def observable_gauge_func(options: CallbackOptions) -> Iterable[Observation]:
    yield Observation(9, {})

# Counter
counter = meter.create_counter("counter")
counter.add(1)

# Async Counter
observable_counter = meter.create_observable_counter(
    "observable_counter", [observable_counter_func]
)

# UpDownCounter
updown_counter = meter.create_up_down_counter("updown_counter")
updown_counter.add(1)
updown_counter.add(-5)

# Async UpDownCounter
observable_updown_counter = meter.create_observable_up_down_counter(
    "observable_updown_counter", [observable_up_down_counter_func]
)

# Histogram
histogram = meter.create_histogram("histogram")
histogram.record(99.9)

# Async Gauge
gauge = meter.create_observable_gauge("gauge", [observable_gauge_func])

input()
