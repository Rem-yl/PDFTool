"""
Service manager for the new extensible architecture
"""

from pathlib import Path
from typing import Optional

from ...core.processor import PDFProcessor
from .service_registry import ServiceRegistry


class ServiceManager:
    """Manager for API services using the new extensible architecture"""

    def __init__(self, temp_dir: Optional[Path] = None):
        self.pdf_processor = PDFProcessor(temp_dir=temp_dir)
        self.service_registry = ServiceRegistry(pdf_processor=self.pdf_processor)

    def get_service_handler(self, service_name: str):
        """Get a service handler by name"""
        return self.service_registry.get_handler(service_name)

    def register_service(self, service_name: str, handler_class: type) -> None:
        """Register a new service handler"""
        self.service_registry.register_handler(service_name, handler_class)

    def list_available_services(self) -> list[str]:
        """List all available services"""
        return self.service_registry.list_services()

    def register_operation(self, operation_type: str, operation_class: type) -> None:
        """Register a new PDF operation"""
        self.pdf_processor.register_operation(operation_type, operation_class)

    def list_available_operations(self) -> list[str]:
        """List all available operations"""
        return self.pdf_processor.get_available_operations()
