import logging
import psutil
import asyncio
from typing import Optional
from src.infrastructure.services.datadog_config import send_metric

logger = logging.getLogger(__name__)


class SystemMetricsCollector:
    """Coletor de métricas de sistema para monitoramento.

    Coleta métricas de CPU, memória e disco, enviando-as
    periodicamente ao Datadog para monitoramento.
    """

    def __init__(self, interval: int = 60):
        """Inicializa o coletor de métricas.

        Args:
            interval (int): Intervalo em segundos entre coletas (padrão: 60).
        """
        self.interval = interval
        self._task: Optional[asyncio.Task] = None
        self.is_running = False

    async def start(self):
        """Inicia a coleta periódica de métricas."""
        if self.is_running:
            logger.warning("SystemMetricsCollector já está em execução")
            return

        self.is_running = True
        self._task = asyncio.create_task(self._collect_loop())
        logger.info(
            f"SystemMetricsCollector iniciado "
            f"com intervalo de {self.interval}s"
        )

    async def stop(self):
        """Para a coleta de métricas."""
        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("SystemMetricsCollector parado")

    async def _collect_loop(self):
        """Loop principal de coleta de métricas."""
        while self.is_running:
            try:
                await self.collect_and_send_metrics()
                await asyncio.sleep(self.interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erro ao coletar métricas: {e}")
                await asyncio.sleep(self.interval)

    async def collect_and_send_metrics(self):
        """Coleta e envia métricas de CPU e RAM."""
        try:
            # Percentual de CPU (não-bloqueante)
            cpu_percent = psutil.cpu_percent(interval=0)
            send_metric(
                "books.system.cpu.percent",
                cpu_percent,
                tags=["resource:cpu"]
            )

            # Percentual de RAM
            memory = psutil.virtual_memory()
            send_metric(
                "books.system.memory.percent",
                memory.percent,
                tags=["resource:memory"]
            )

            logger.debug("Métricas de sistema enviadas com sucesso")

        except Exception as e:
            logger.error(f"Erro ao enviar métricas de sistema: {e}")


# Instância global do coletor
_system_metrics_collector: Optional[SystemMetricsCollector] = None


def get_system_metrics_collector(interval: int = 60) -> SystemMetricsCollector:
    """Obtém a instância do coletor de métricas de sistema.

    Args:
        interval (int): Intervalo de coleta em segundos.

    Returns:
        SystemMetricsCollector: Instância do coletor.
    """
    global _system_metrics_collector
    if _system_metrics_collector is None:
        _system_metrics_collector = SystemMetricsCollector(interval)
    return _system_metrics_collector
