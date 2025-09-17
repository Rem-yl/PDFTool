"""
Service registry for API handlers
"""

from typing import Dict, Type

from .interfaces import IServiceHandler, IServiceRegistry


class ServiceRegistry(IServiceRegistry):
    """Registry for API service handlers"""

    def __init__(self, pdf_processor=None):
        self.pdf_processor = pdf_processor
        self._handlers: Dict[str, Type[IServiceHandler]] = {}
        self._register_default_handlers()

    def register_handler(self, service_name: str, handler_class: Type[IServiceHandler]) -> None:
        """Register a service handler"""
        self._handlers[service_name] = handler_class

    def get_handler(self, service_name: str) -> IServiceHandler:
        """Get a service handler by name"""
        if service_name not in self._handlers:
            raise ValueError(f"Unknown service: {service_name}")

        handler_class = self._handlers[service_name]
        return handler_class(pdf_processor=self.pdf_processor)

    def list_services(self) -> list[str]:
        """List all registered services"""
        return list(self._handlers.keys())

    def _register_default_handlers(self) -> None:
        """Register default service handlers"""
        # Import here to avoid circular imports
        from .handlers.info import InfoServiceHandler
        from .handlers.merge import MergeServiceHandler
        from .handlers.split import SplitServiceHandler
        from .handlers.watermark import WatermarkServiceHandler

        self.register_handler("merge", MergeServiceHandler)
        self.register_handler("split", SplitServiceHandler)
        self.register_handler("info", InfoServiceHandler)
        self.register_handler("watermark", WatermarkServiceHandler)
