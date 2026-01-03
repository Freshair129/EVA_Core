from typing import Optional, Dict, Any

class MSPError(Exception):
    """Base class for MSP-related errors"""
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        self.message = message
        self.context = context or {}
        super().__init__(self.message)

class MSPValidationError(MSPError):
    """Raised when data validation fails against schema"""
    pass

class StructuralValidationError(MSPValidationError):
    """Raised when JSON structure is invalid"""
    pass

class MSPConsolidationError(MSPError):
    """Raised when consolidation fails"""
    pass

class MSPBackupError(MSPError):
    """Raised when backup fails"""
    pass
