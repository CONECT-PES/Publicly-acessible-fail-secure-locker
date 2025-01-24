from typing import Generic, TypeVar, Union

T = TypeVar('T')

class Result(Generic[T]):
    def __init__(self, value: Union[T, None] = None, error: str = None):
        self.value = value
        self.error = error

    @property
    def is_success(self) -> bool:
        return self.error is None

    @property
    def is_failure(self) -> bool:
        return self.error is not None