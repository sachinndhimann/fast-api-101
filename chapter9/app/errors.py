"""
Custom exception hierarchy. Routes/services raise these; a global handler
(registered in main.py) turns them into a CONSISTENT JSON error envelope.
This is the payoff of chapter 2's "error responses" design guide, implemented.
"""

class AppError(Exception):
    """Base class for all our domain errors."""
    status_code = 500
    code = "INTERNAL_ERROR"

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundError(AppError):
    status_code = 404
    code = "NOT_FOUND"


class ValidationError(AppError):
    status_code = 400
    code = "VALIDATION_ERROR"


class ConflictError(AppError):
    status_code = 409
    code = "CONFLICT"


class OutOfStockError(AppError):
    status_code = 400
    code = "OUT_OF_STOCK"
