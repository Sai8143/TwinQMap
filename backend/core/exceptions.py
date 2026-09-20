from typing import Any, Dict, Optional

class TwinQMapException(Exception):
    """
    Base exception class for all custom TwinQ-Map application errors.
    """
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        detail: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.detail = detail or {}


class DatabaseException(TwinQMapException):
    """
    Exception raised during MongoDB database queries, inserts, or index errors.
    """
    def __init__(self, message: str, detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=503, detail=detail)


class QuantumAPIException(TwinQMapException):
    """
    Exception raised when interacting with external quantum cloud providers (IBM, IonQ, Azure, AWS).
    """
    def __init__(self, message: str, provider: str, detail: Optional[Dict[str, Any]] = None):
        merged_detail = {"provider": provider}
        if detail:
            merged_detail.update(detail)
        super().__init__(message, status_code=502, detail=merged_detail)


class PredictionException(TwinQMapException):
    """
    Exception raised during machine learning predictions or digital twin state forecasts.
    """
    def __init__(self, message: str, detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=422, detail=detail)


class SchedulerException(TwinQMapException):
    """
    Exception raised during the mapping, cost analysis, or qubit scheduler execution phases.
    """
    def __init__(self, message: str, detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, detail=detail)


class ValidationException(TwinQMapException):
    """
    Exception raised when validation of configurations, request schemas, or circuit inputs fails.
    """
    def __init__(self, message: str, detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=422, detail=detail)


class AuthenticationException(TwinQMapException):
    """
    Exception raised when JWT token is invalid, expired, or missing.
    """
    def __init__(self, message: str, detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=401, detail=detail)


class NotAuthorizedException(TwinQMapException):
    """
    Exception raised when an authenticated user does not have sufficient role permissions.
    """
    def __init__(self, message: str = "Permission denied", detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=403, detail=detail)


class NotFoundException(TwinQMapException):
    """
    Exception raised when a requested resource (e.g. Qubit configuration, Job ID) is not found.
    """
    def __init__(self, message: str, detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=404, detail=detail)
