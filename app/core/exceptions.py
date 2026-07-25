class NotFoundError(Exception):
    """Raised when a requested resource cannot be found."""

    def __init__(self, message: str = "Resource not found") -> None:
        self.message = message
        super().__init__(message)

    @property
    def status_code(self) -> int:
        return 404
