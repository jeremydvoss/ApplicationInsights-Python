# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------
import importlib

from typing import Any, Dict
from logging import NOTSET, getLogger

from azure.monitor.opentelemetry.distro.util import get_configurations
from azure.monitor.opentelemetry.exporter import (
    ApplicationInsightsSampler,
    AzureMonitorLogExporter,
    AzureMonitorTraceExporter,
)
from opentelemetry.sdk._logs import (
    LoggerProvider,
    LoggingHandler,
    get_logger_provider,
    set_logger_provider,
)
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.trace import get_tracer_provider, set_tracer_provider

_logger = getLogger(__name__)


_SUPPORTED_INSTRUMENTED_LIBRARIES = {
    "django",
    "flask",
    "psycopg2",
    "requests",
}


def configure_azure_monitor(**kwargs):
    """
    This function works as a configuration layer that allows the
    end user to configure OpenTelemetry and Azure monitor components. The
    configuration can be done via arguments passed to this function.
    """

    configurations = get_configurations(**kwargs)

    disable_tracing = configurations.get("disable_tracing", False)
    disable_logging = configurations.get("disable_logging", False)

    resource = None
    if not disable_logging or not disable_tracing:
        resource = _get_resource(configurations) 

    # Setup tracing pipeline
    if not disable_tracing:
        _setup_tracing(resource, configurations, **kwargs)

    # Setup logging pipeline
    if not disable_logging:
        _setup_logging(resource, configurations, **kwargs)

    # Setup instrumentations
    # Instrumentations need to be setup last so to use the global providers
    # instanstiated in the other setup steps
    _setup_instrumentations(configurations.get("instrumentations", []))


def _get_resource(configurations: Dict[str, Any]) -> Resource:
    service_name = configurations.get("service_name", "")
    service_namespace = configurations.get("service_namespace", "")
    service_instance_id = configurations.get("service_instance_id", "")
    return Resource.create(
            {
                ResourceAttributes.SERVICE_NAME: service_name,
                ResourceAttributes.SERVICE_NAMESPACE: service_namespace,
                ResourceAttributes.SERVICE_INSTANCE_ID: service_instance_id,
            }
        )


def _setup_tracing(resource: Resource, configurations: Dict[str, Any], **kwargs: Dict[Any, Any]):
    sampling_ratio = configurations.get("sampling_ratio", 1.0)
    tracing_export_interval_millis = configurations.get(
        "tracing_export_interval_millis", 30000
    )
    tracer_provider = TracerProvider(
            sampler=ApplicationInsightsSampler(sampling_ratio=sampling_ratio),
            resource=resource,
        )
    set_tracer_provider(tracer_provider)
    trace_exporter = AzureMonitorTraceExporter(**kwargs)
    span_processor = BatchSpanProcessor(
        trace_exporter,
        export_timeout_millis=tracing_export_interval_millis,
    )
    get_tracer_provider().add_span_processor(span_processor)


def _setup_logging(resource: Resource, configurations: Dict[str, Any], **kwargs: Dict[Any, Any]):
    logging_level = configurations.get("logging_level", NOTSET)
    logging_export_interval_millis = configurations.get(
        "logging_export_interval_millis", 30000
    )
    logger_provider = LoggerProvider(resource=resource)
    set_logger_provider(logger_provider)
    log_exporter = AzureMonitorLogExporter(**kwargs)
    log_record_processor = BatchLogRecordProcessor(
        log_exporter,
        export_timeout_millis=logging_export_interval_millis,
    )
    get_logger_provider().add_log_record_processor(log_record_processor)
    handler = LoggingHandler(
        level=logging_level, logger_provider=get_logger_provider()
    )
    getLogger().addHandler(handler)


def _setup_instrumentations(instrumentations: Dict[str, str]):
    for lib_name in instrumentations:
        if lib_name in _SUPPORTED_INSTRUMENTED_LIBRARIES:
                try:
                    importlib.import_module(lib_name)
                except ImportError as ex:
                    _logger.warning(
                        "Unable to import %s. Please make sure it is installed.",
                        lib_name
                    )
                    continue
                instr_lib_name = "opentelemetry.instrumentation." + lib_name
                try:
                    module = importlib.import_module(instr_lib_name)
                    instrumentor_name = "{}Instrumentor".format(
                        lib_name.capitalize()
                    )
                    class_ = getattr(module, instrumentor_name)
                    class_().instrument()
                except ImportError:
                    _logger.warning(
                        "Unable to import %s. Please make sure it is installed.",
                        instr_lib_name
                    )
                except Exception as ex:
                    _logger.warning(
                        "Exception occured when instrumenting: %s.", lib_name, exc_info=ex)
                finally:
                    continue
        else:
            _logger.warning("Instrumentation not supported for library: %s.", lib_name)
