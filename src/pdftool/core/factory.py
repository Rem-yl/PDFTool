"""
Factory for creating and managing PDF operations
"""

from pathlib import Path
from typing import Dict, Optional, Type

from ..common.interfaces import IPDFOperation, IPDFOperationFactory


class PDFOperationFactory(IPDFOperationFactory):
    """Factory for creating PDF operations using registry pattern"""

    def __init__(self, temp_dir: Optional[Path] = None):
        self.temp_dir = temp_dir or Path("temp")
        self._operations: Dict[str, Type[IPDFOperation]] = {}
        self._register_default_operations()

    def create_operation(self, operation_type: str) -> IPDFOperation:
        """Create a specific PDF operation"""
        if operation_type not in self._operations:
            raise ValueError(f"Unknown operation type: {operation_type}")

        operation_class = self._operations[operation_type]
        return operation_class(temp_dir=self.temp_dir)

    def register_operation(self, operation_type: str, operation_class: Type[IPDFOperation]) -> None:
        """Register a new operation type"""
        self._operations[operation_type] = operation_class

    def list_operations(self) -> list[str]:
        """List all available operation types"""
        return list(self._operations.keys())

    def _register_default_operations(self) -> None:
        """Register default operations"""
        # Import here to avoid circular imports
        from ..domains.document.operations.info import InfoOperation
        from ..domains.document.operations.merge import MergeOperation
        from ..domains.document.operations.split import SplitOperation
        from ..domains.document.operations.watermark import WatermarkOperation

        self.register_operation("merge", MergeOperation)
        self.register_operation("split", SplitOperation)
        self.register_operation("info", InfoOperation)
        self.register_operation("watermark", WatermarkOperation)
