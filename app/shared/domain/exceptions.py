# app/shared/domain/exceptions.py

class DomainException(Exception):
    """Base class for domain-specific exceptions within the application."""
    def __init__(self, message="A domain error occurred."):
        super().__init__(message)

class TemplateNotFound(DomainException):
    """Raised when a requested template cannot be found."""
    def __init__(self, template_id: int = None, message="Template not found."):
        if template_id:
            message = f"Template with ID {template_id} not found."
        super().__init__(message)
        self.template_id = template_id

class PermissionDenied(DomainException):
    """Raised when an action is denied due to insufficient permissions."""
    def __init__(self, user_id: str = None, action: str = None, message="Permission denied."):
        details = []
        if user_id:
            details.append(f"User ID: {user_id}")
        if action:
            details.append(f"Action: {action}")
        
        if details:
            message = f"Permission denied ({', '.join(details)})."
        super().__init__(message)
        self.user_id = user_id
        self.action = action

class InvalidOperation(DomainException):
    """Raised when an operation is attempted that is invalid in the current state."""
    def __init__(self, message="Invalid operation attempted."):
        super().__init__(message)

# Add more specific exceptions as needed, inheriting from DomainException 