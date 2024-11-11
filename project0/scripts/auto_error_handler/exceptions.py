
class AutoErrorHandlerException(Exception):
    """Base exception for auto error handler"""
    pass

class FixApplicationError(AutoErrorHandlerException):
    """Raised when fix application fails"""
    pass

class ValidationError(AutoErrorHandlerException):
    """Raised when fix validation fails"""
    pass

class AIServiceError(AutoErrorHandlerException):
    """Raised when AI service interaction fails"""
    pass