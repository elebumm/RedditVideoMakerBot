from attr import attrs, attrib
from typing import TypeVar, Optional, Callable, Union


_function = TypeVar("_function", bound=Callable[..., object])
_exceptions = TypeVar("_exceptions", bound=Optional[Union[type, tuple, list]])


@attrs
class ExceptionDecorator:
    """
    Decorator factory for catching exceptions and writing logs
    """
    exception: Optional[_exceptions] = attrib(default=None)
    _default_exception: Optional[_exceptions] = attrib(
        kw_only=True,
        default=None
    )

    def __attrs_post_init__(self):
        if not self.exception:
            self.exception = self._default_exception

    def __call__(
            self,
            func: _function,
    ):
        async def wrapper(*args, **kwargs):
            try:
                obj_to_return = await func(*args, **kwargs)
                return obj_to_return
            except Exception as caughtException:
                import logging

                logger = logging.getLogger("webdriver_log")
                logger.setLevel(logging.ERROR)
                handler = logging.FileHandler(".webdriver.log", mode="a+", encoding="utf-8")
                logger.addHandler(handler)

                if isinstance(self.exception, type):
                    if not type(caughtException) == self.exception:
                        logger.error(f"unexpected error - {caughtException}")
                else:
                    if not type(caughtException) in self.exception:
                        logger.error(f"unexpected error - {caughtException}")

        return wrapper

    @classmethod
    def catch_exception(
            cls,
            func: Optional[_function],
            exception: Optional[_exceptions] = None,
    ) -> Union[object, _function]:
        """
        Decorator for catching exceptions and writing logs

        Args:
            func: Function to be decorated
            exception: Expected exception(s)
        Returns:
            Decorated function
        """
        exceptor = cls(exception)
        if func:
            exceptor = exceptor(func)
        return exceptor
