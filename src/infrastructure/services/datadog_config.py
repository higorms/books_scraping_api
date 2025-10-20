import os
import logging
from typing import List, Optional
from datetime import datetime
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v2.api.metrics_api import MetricsApi
from datadog_api_client.v2.model.metric_intake_type import MetricIntakeType
from datadog_api_client.v2.model.metric_payload import MetricPayload
from datadog_api_client.v2.model.metric_point import MetricPoint
from datadog_api_client.v2.model.metric_resource import MetricResource
from datadog_api_client.v2.model.metric_series import MetricSeries
from datadog_api_client.v2.api.logs_api import LogsApi
from datadog_api_client.v2.model.http_log import HTTPLog
from datadog_api_client.v2.model.http_log_item import HTTPLogItem
from ddtrace import tracer, patch_all


logger = logging.getLogger(__name__)


class DatadogService:
    """Serviço para integração com a API do Datadog."""

    _instance = None
    _client: Optional[ApiClient] = None
    _metrics_api: Optional[MetricsApi] = None
    _logs_api: Optional[LogsApi] = None
    _enabled: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatadogService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Inicializa o serviço Datadog."""
        if self._client is None:
            return

        dd_api_key = os.getenv("DATADOG_API_KEY")
        dd_app_key = os.getenv("DATADOG_APP_KEY")
        dd_site = "datadoghq.com"

        if not dd_api_key:
            logger.warning(
                "DD_API_KEY não configurada. "
                "Monitoramento Datadog desabilitado."
            )
            self._enabled = False
            return

        try:
            # Configura o cliente da API do Datadog
            configuration = Configuration()
            configuration.api_key["apiKeyAuth"] = dd_api_key
            if dd_app_key:
                configuration.api_key["appKeyAuth"] = dd_app_key
            configuration.server_variables["site"] = dd_site

            self._client = ApiClient(configuration)
            self._metrics_api = MetricsApi(self._client)
            self._logs_api = LogsApi(self._client)

            patch_all()

            self._enabled = True
            logger.info(
                "Datadog configurado com sucesso."
            )

        except Exception as e:
            logger.error(
                f"Erro ao configurar Datadog: {e}"
            )
            self._enabled = False

    def is_enbled(self) -> bool:
        """Verifica se o Datadog está habilitado."""
        return self._enabled

    def submit_metric(
        self,
        metric_name: str,
        value: float,
        metric_type: str = "gauge",
        tags: Optional[List[str]] = None,
        timestamp: Optional[int] = None
    ):
        """Envia uma méttrica para o Datadog.

        Args:
            metric_name: Nome da métrica (ex: 'books.search.count')
            value: Valor da métrica
            metric_type: Tipo da métrica ('gauge', 'count', 'rate')
            tags: Lista de tags (ex: ['env:production', 'service:api'])
            timestamp: Unix timestamp (opcional, usa tempo atual se None)
        """
        if not self._enabled:
            return
        
        try:
            if timestamp is None:
                timestamp = int(datetime.now().timestamp())
            
            # Define o tipo de métrica
            intake_type = MetricIntakeType.GAUGE
            if metric_type == "count":
                intake_type = MetricIntakeType.COUNT
            elif metric_type == "rate":
                intake_type = MetricIntakeType.RATE
                
            # Adiciona tags padrão
            default_tags = [
                f"service:{os.getenv('DD_SERVICE', 'books-scraping-api')}",
                f"env:{os.getenv('DD_ENV', 'production')}",
                f"version:{os.getenv('DD_VERSION', '1.0.0')}"
            ]
            all_tags = default_tags + (tags or [])
            
            # Cria o payload da métrica
            series = MetricSeries(
                metric=metric_name,
                type=intake_type,
                points=[
                    MetricPoint(
                        timestamp=timestamp,
                        value=value,
                    )
                ],
                tags=all_tags,
            )
            

            payload = MetricPayload(
                series=[series]
            )
            
            # Envia a métrica
            self._metrics_api.submit_metrics(body=payload)
            logger.debug(f"Métrica enviada: {metric_name}={value} tags={all_tags}")
            
        except Exception as e:
            logger.error(f"Erro ao enviar métrica {metric_name}: {e}")
    
    def increment_counter(
            self,
            metric_name: str,
            value: int = 1,
            tags: Optional[List[str]] = None
        ):
            """Incrementa um contador no Datadog.
            
            Args:
                metric_name: Nome do contador
                value: Valor a incrementar (padrão: 1)
                tags: Lista de tags
            """
            self.submit_metric(metric_name, value, metric_type="count", tags=tags)
    
    def send_gauge(
        self,
        metric_name: str,
        value: float,
        tags: Optional[List[str]] = None
    ):
        """Envia um gauge para o Datadog.
       
        Args:
            metric_name: Nome da métrica
            value: Valor atual
            tags: Lista de tags
        """
        self.submit_metric(metric_name, value, metric_type="gauge", tags=tags)

    def send_log(
        self,
        message: str,
        level: str = "info",
        tags: Optional[List[str]] = None,
        attributes: Optional[dict] = None
    ):
        """Envia um log para o Datadog.
        
        Args:
            message: Mensagem do log
            level: Nível do log (debug, info, warn, error)
            tags: Lista de tags
            attributes: Atributos adicionais do log
        """
        if not self._enabled:
            return
        
        try:
            # Adiciona tags padrão
            default_tags = [
                f"service:{os.getenv('DD_SERVICE', 'books-scraping-api')}",
                f"env:{os.getenv('DD_ENV', 'production')}",
                f"version:{os.getenv('DD_VERSION', '1.0.0')}"
            ]
            all_tags = ",".join(default_tags + (tags or []))
            
            # Monta os atributos do log
            log_attributes = {
                "level": level,
                "timestamp": datetime.now().isoformat(),
                **(attributes or {})
            }
            
            # Cria o item de log
            log_item = HTTPLogItem(
                ddsource="python",
                ddtags=all_tags,
                message=message,
                service=os.getenv('DD_SERVICE', 'books-scraping-api'),
                **log_attributes
            )

            # Envia o log
            body = HTTPLog([log_item])
            self._logs_api.submit_log(body=body)
            logger.debug(f"Log enviado para Datadog: {message}")
            
        except Exception as e:
            logger.error(f"Erro ao enviar log para Datadog: {e}")

           
# Singleton instance
_datadog_service = DatadogService()


def configure_datadog():
    """Configura a integração com Datadog."""
    return _datadog_service.is_enabled()


def send_metric(metric_name: str, value: float, tags: Optional[List[str]] = None):
    """Wrapper para enviar métrica gauge."""
    _datadog_service.send_gauge(metric_name, value, tags)


def increment_counter(metric_name: str, value: int = 1, tags: Optional[List[str]] = None):
    """Wrapper para incrementar contador."""
    _datadog_service.increment_counter(metric_name, value, tags)


def send_log(message: str, level: str = "info", tags: Optional[List[str]] = None, attributes: Optional[dict] = None):
    """Wrapper para enviar log."""
    _datadog_service.send_log(message, level, tags, attributes)