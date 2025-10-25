import logging
from src.infrastructure.services.datadog_config import send_log


class DatadogLogHandler(logging.Handler):
    """Handler customizado para enviar logs ao Datadog."""

    def emit(self, record: logging.LogRecord):
        """Envia o log para o Datadog."""
        try:
            # Monta os atributos do log
            attributes = {
                "logger.name": record.name,
                "logger.thread_name": record.threadName,
                "logger.method_name": record.funcName,
            }

            # Adiciona informações extras se houver
            if hasattr(record, 'pathname'):
                attributes["logger.file_name"] = record.pathname
                attributes["logger.line_number"] = record.lineno

            # Adiciona informações de exceção, se houver
            if record.exc_info:
                attributes["error.kind"] = record.exc_info[0].__name__
                attributes["error.message"] = str(record.exc_info[1])
                # Usa formatException ao invés de format para evitar duplicação
                attributes["error.stack"] = self.formatException(record.exc_info)

            # Envia o log para o Datadog (SEM passar status como atributo separado)
            send_log(
                message=record.getMessage(),
                level=record.levelname.lower(),
                attributes=attributes
            )
        except Exception as e:
            # Usa handleError para não quebrar a aplicação
            self.handleError(record)
            # Log apenas no console para debug
            print(f"Erro ao enviar log para Datadog: {e}")
