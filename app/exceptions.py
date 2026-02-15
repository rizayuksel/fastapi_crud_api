class AppException(Exception):
    # The parent of all my custom headaches
    def __init__(self, message: str, status_code: int = 400, code: str = "BAD_REQUEST"):
        self.message = message
        self.status_code = status_code
        self.code = code
        super().__init__(self.message)


class ResourceNotFoundError(AppException):
    # Use this when something is missing in the DB
    def __init__(self, resource: str, identifier: any):
        super().__init__(
            message=f"{resource} with id {identifier} not found", status_code=404, code="NOT_FOUND"
        )


class AuthenticationError(AppException):
    # For when users forget their own passwords...
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message=message, status_code=401, code="AUTH_FAILED")
