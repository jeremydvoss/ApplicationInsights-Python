# Copyright The OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from unittest.mock import Mock, patch

from azure.monitor.opentelemetry.distro import configure_azure_monitor
from opentelemetry.semconv.resource import ResourceAttributes


class TestConfigure(unittest.TestCase):
    @patch(
        "azure.monitor.opentelemetry.distro.BatchSpanProcessor",
    )
    @patch(
        "azure.monitor.opentelemetry.distro.AzureMonitorTraceExporter",
    )
    @patch(
        "azure.monitor.opentelemetry.distro.TracerProvider",
        autospec=True,
    )
    @patch(
        "azure.monitor.opentelemetry.distro.ApplicationInsightsSampler",
    )
    @patch(
        "azure.monitor.opentelemetry.distro.Resource",
    )
    @patch(
        "azure.monitor.opentelemetry.distro.trace",
    )
    def test_configure_azure_monitor(
        self,
        trace_mock,
        resource_mock,
        sampler_mock,
        tp_mock,
        exporter_mock,
        bsp_mock,
    ):
        tp_init_mock = Mock()
        tp_mock.return_value = tp_init_mock
        exp_init_mock = Mock()
        exporter_mock.return_value = exp_init_mock
        resource_init_mock = Mock()
        resource_mock.create.return_value = resource_init_mock
        sampler_init_mock = Mock()
        sampler_mock.return_value = sampler_init_mock
        bsp_init_mock = Mock()
        bsp_mock.return_value = bsp_init_mock
        configure_azure_monitor(
            disable_tracing=False,
            service_name="test_service_name",
            service_namespace="test_namespace",
            service_instance_id="test_id",
            sampling_ratio=0.5,
            tracing_export_interval_millis=15000,
        )
        resource_mock.create.assert_called_once_with(
            {
                ResourceAttributes.SERVICE_NAME: "test_service_name",
                ResourceAttributes.SERVICE_NAMESPACE: "test_namespace",
                ResourceAttributes.SERVICE_INSTANCE_ID: "test_id",
            }
        )
        tp_mock.assert_called_once_with(
            sampler=sampler_init_mock,
            resource=resource_init_mock,
        )
        trace_mock.set_tracer_provider.assert_called_once_with(tp_init_mock)
        exporter_mock.assert_called_once()
        sampler_mock.assert_called_once_with(sampling_ratio=0.5)
        bsp_mock.assert_called_once_with(
            exp_init_mock,
            export_timeout_millis=15000,
        )

    @patch(
        "azure.monitor.opentelemetry.distro.BatchSpanProcessor",
    )
    @patch(
        "azure.monitor.opentelemetry.distro.AzureMonitorTraceExporter",
    )
    @patch(
        "azure.monitor.opentelemetry.distro.TracerProvider",
        autospec=True,
    )
    @patch(
        "azure.monitor.opentelemetry.distro.ApplicationInsightsSampler",
    )
    @patch(
        "azure.monitor.opentelemetry.distro.Resource",
    )
    @patch(
        "azure.monitor.opentelemetry.distro.trace",
    )
    def test_configure_azure_monitor_disable_tracing(
        self,
        trace_mock,
        resource_mock,
        sampler_mock,
        tp_mock,
        exporter_mock,
        bsp_mock,
    ):
        configure_azure_monitor(
            disable_tracing=True,
        )
        resource_mock.assert_not_called()
        tp_mock.assert_not_called()
        trace_mock.set_tracer_provider.assert_not_called()
        sampler_mock.assert_not_called()
        exporter_mock.assert_not_called()
        bsp_mock.assert_not_called()

    @patch(
        "azure.monitor.opentelemetry.distro.BatchSpanProcessor",
    )
    @patch(
        "azure.monitor.opentelemetry.distro.AzureMonitorTraceExporter",
    )
    @patch(
        "azure.monitor.opentelemetry.distro.TracerProvider",
        autospec=True,
    )
    @patch(
        "azure.monitor.opentelemetry.distro.ApplicationInsightsSampler",
    )
    @patch(
        "azure.monitor.opentelemetry.distro.Resource",
    )
    @patch(
        "azure.monitor.opentelemetry.distro.trace",
    )
    def test_configure_azure_monitor_exporter(
        self,
        trace_mock,
        resource_mock,
        sampler_mock,
        tp_mock,
        exporter_mock,
        bsp_mock,
    ):
        tp_init_mock = Mock()
        tp_mock.return_value = tp_init_mock
        exp_init_mock = Mock()
        exporter_mock.return_value = exp_init_mock
        resource_init_mock = Mock()
        resource_mock.create.return_value = resource_init_mock
        sampler_init_mock = Mock()
        sampler_mock.return_value = sampler_init_mock
        bsp_init_mock = Mock()
        bsp_mock.return_value = bsp_init_mock
        kwargs = {
            "connection_string": "test_cs",
            "api_version": "1.0",
            "disable_offline_storage": True,
            "storage_maintenance_period": 50,
            "storage_max_size": 1024,
            "storage_min_retry_interval": 30,
            "storage_directory": "/tmp",
            "storage_retention_period": 60,
            "timeout": 30,
        }
        configure_azure_monitor(**kwargs)
        resource_mock.create.assert_called_once()
        tp_mock.assert_called_once()
        trace_mock.set_tracer_provider.assert_called_once()
        exporter_mock.assert_called_once_with(**kwargs)
        sampler_mock.assert_called_once()
        bsp_mock.assert_called_once()