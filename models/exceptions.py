class ObjectNotFoundException(Exception):
    def __init__(self, message: str = "Object not found", *args: object) -> None:
        super().__init__(message, *args)
