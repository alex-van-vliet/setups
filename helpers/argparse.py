from typing import Callable


def check_to_type(check: Callable[[str], bool], message: str):
    def type_fn(value: str):
        if not check(value):
            raise ValueError(message)
        return value

    return type_fn
