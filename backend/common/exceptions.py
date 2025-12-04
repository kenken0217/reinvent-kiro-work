"""
Custom domain exceptions
"""


class DomainException(Exception):
    """Base exception for all domain errors"""
    pass


class NotFoundError(DomainException):
    """Raised when a requested resource is not found"""
    pass


class ConflictError(DomainException):
    """Raised when there is a conflict (e.g., duplicate resource)"""
    pass


class ValidationError(DomainException):
    """Raised when validation fails"""
    pass


class CapacityError(DomainException):
    """Raised when capacity limits are exceeded"""
    pass
