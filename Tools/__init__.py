from agents import function_tool as _function_tool
from typing import Any, Callable


def function_tool(*dargs: Any, name: str | None = None, description: str | None = None, **dkwargs: Any) -> Callable:
    """
    Wrapper around agents.function_tool that accepts optional name and description
    arguments. If the underlying SDK doesn't support these parameters, they're
    attached manually to the resulting tool.
    """

    if dargs and callable(dargs[0]) and len(dargs) == 1 and not dkwargs:
        # Used as @function_tool without parentheses
        func = dargs[0]
        decorated = _function_tool(func)
        if name:
            setattr(decorated, "name", name)
        if description:
            setattr(decorated, "description", description)
        return decorated

    def _decorator(func: Callable) -> Callable:
        try:
            decorated = _function_tool(name=name, description=description, **dkwargs)(func)
        except TypeError:
            decorated = _function_tool(**dkwargs)(func)
            if name:
                setattr(decorated, "name", name)
            if description:
                setattr(decorated, "description", description)
        return decorated

    return _decorator

