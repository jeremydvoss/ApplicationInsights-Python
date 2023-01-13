from unittest import TestCase
from unittest.mock import patch

from azure.monitor.opentelemetry.distro.distro import AzureMonitorDistro


class TestDistro(TestCase):
    @patch(
        "azure.monitor.opentelemetry.distro.distro.AzureDiagnosticLogging.enable"
    )
    # TODO: Enabled when duplciate logging issue is solved
    # @patch(
    #     "azure.monitor.opentelemetry.distro._diagnostic_logging._EXPORTER_DIAGNOSTICS_ENABLED",
    #     False,
    # )
    def test_configure(self, mock_diagnostics):
        distro = AzureMonitorDistro()
        distro.configure()
        self.assertEqual(mock_diagnostics.call_count, 2)

    # TODO: Enabled when duplciate logging issue is solved
    # @patch(
    #     "azure.monitor.opentelemetry.distro.distro.AzureDiagnosticLogging.enable"
    # )
    # @patch(
    #     "azure.monitor.opentelemetry.distro._diagnostic_logging._EXPORTER_DIAGNOSTICS_ENABLED",
    #     True,
    # )
    # def test_configure_exporter_diagnostics(self, mock_diagnostics):
    #     distro = AzureMonitorDistro()
    #     distro.configure()
    #     self.assertEqual(mock_diagnostics.call_count, 3)
