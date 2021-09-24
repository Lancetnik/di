from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, Generic, List

from anydep._inspect import DependencyParameter, ParameterKind
from anydep.dependency import Dependency, DependencyType

_UNSET = object()


class Task(Generic[DependencyType]):
    def __init__(
        self,
        call: Callable[..., Awaitable[DependencyType]],
        dependencies: Dict[str, DependencyParameter[Task[Dependency]]],
    ) -> None:
        self.call = call
        self.dependencies = dependencies
        self._result: Any = _UNSET

    async def compute(self):
        positional: List[Task[Dependency]] = []
        keyword: Dict[str, Task[Dependency]] = {}
        for k, v in self.dependencies.items():
            if v.kind is ParameterKind.positional:
                positional.append(v.dependency.get_result())
            else:
                keyword[k] = v.dependency.get_result()
        self._result = await self.call(*positional, **keyword)

    def get_result(self):
        if self._result is _UNSET:
            raise ValueError(
                "`compute()` must be called before `get_result()`; this is likely a bug!"
            )
        return self._result
