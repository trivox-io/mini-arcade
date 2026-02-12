"""
Typed, safe, and subclass-isolated implementation registry.
"""

from __future__ import annotations

import re
import threading
from abc import ABC
from typing import (
    Callable,
    ClassVar,
    Generic,
    Iterator,
    Mapping,
    MutableMapping,
    Optional,
    Type,
    TypeVar,
)

# pylint: disable=invalid-name
ImplementationType = TypeVar(
    "ImplementationType"
)  # implementation type (classes deriving from implementation_base)
# pylint: enable=invalid-name


class ImplementationRegistry(Generic[ImplementationType]):
    """
    A registry of *classes* implementing a specific interface.

    Subclasses **must** set `implementation_base` to the ABC (or base class) that all
    implementations derive from.

    :ivar implementation_base: ClassVar[type]: The base class for registered implementations.
    :ivar _registry: ClassVar[MutableMapping[str, Type[ImplementationType]]]: Mapping of names to
        implementation classes.
    :ivar _lock: ClassVar[threading.RLock]: Lock for thread-safe operations.
    """

    implementation_base: ClassVar[type] = ABC  # override in subclasses
    _registry: ClassVar[MutableMapping[str, Type[ImplementationType]]]
    _lock: ClassVar[threading.RLock]

    def __init_subclass__(cls, **kwargs):  # type: ignore[override]
        super().__init_subclass__(**kwargs)
        cls._registry = {}
        cls._lock = threading.RLock()

    @staticmethod
    def _infer_name(impl_class: type) -> str:
        return impl_class.__name__.lower()

    @classmethod
    def register(
        cls,
        name: str,
        impl_class: Type[ImplementationType],
        *,
        replace: bool = False,
    ):
        """
        Register an implementation implementation class.

        :param name: Name to register the implementation under.
        :type name: str

        :param impl_class: Implementation class to register.
        :type impl_class: Type[ImplementationType]

        :param replace: Whether to replace an existing registration.
        :type replace: bool

        :raises TypeError: If `impl_class` does not subclass `implementation_base`.
        :raises KeyError: If `name` is already registered and `replace` is False
        """
        if not issubclass(impl_class, cls.implementation_base):
            raise TypeError(
                f"{impl_class.__qualname__} must subclass {cls.implementation_base.__qualname__}"
            )
        with cls._lock:
            if not replace and name in cls._registry:
                raise KeyError(f"Implementation '{name}' already registered")
            cls._registry[name] = impl_class

    @classmethod
    def unregister(cls, name: str):
        """
        Unregister an implementation implementation by name.

        :param name: Name of the implementation to unregister.
        :type name: str
        """
        with cls._lock:
            cls._registry.pop(name, None)

    @classmethod
    def implementation(
        cls, name: Optional[str] = None, *, replace: bool = False
    ) -> Callable[[Type[ImplementationType]], Type[ImplementationType]]:
        """
        Decorator to register an implementation implementation class.

        :param name: Name to register the implementation under.
        :type name: Optional[str]

        :param replace: Whether to replace an existing registration.
        :type replace: bool
        """

        def decorator(
            impl_class: Type[ImplementationType],
        ) -> Type[ImplementationType]:
            cls.register(
                name or cls._infer_name(impl_class),
                impl_class,
                replace=replace,
            )
            return impl_class

        return decorator

    @classmethod
    def get(cls, name: str) -> Type[ImplementationType]:
        """
        Get the implementation implementation class by name.

        :param name: Name of the implementation to retrieve.
        :type name: str

        :return: Implementation class.
        :rtype: Type[ImplementationType]

        :raises KeyError: If the name is not registered.
        """
        try:
            return cls._registry[name]
        except KeyError as e:
            raise KeyError(f"Unknown implementation '{name}'") from e

    @classmethod
    def try_get(cls, name: str) -> Optional[Type[ImplementationType]]:
        """
        Try to get the implementation implementation class by name.

        :param name: Name of the implementation to retrieve.
        :type name: str

        :return: Implementation class or None if not found.
        :rtype: Optional[Type[ImplementationType]]
        """
        return cls._registry.get(name, None)

    @classmethod
    def contains(cls, name: str) -> bool:
        """
        Check if an implementation implementation is registered by name.

        :param name: Name of the implementation to check.
        :type name: str

        :return: True if registered, False otherwise.
        :rtype: bool
        """
        return name in cls._registry

    @classmethod
    def all(cls) -> Mapping[str, Type[ImplementationType]]:
        """
        Get a mapping of all registered implementation implementations.

        :return: Mapping of names to implementation classes.
        :rtype: Mapping[str, Type[ImplementationType]]
        """
        return dict(cls._registry)

    @classmethod
    def names(cls) -> list[str]:
        """
        Get a list of all registered implementation implementation names.

        :return: List of implementation names.
        :rtype: list[str]
        """
        return list(cls._registry.keys())

    @classmethod
    def find_contains(cls, needle: str) -> list[Type[ImplementationType]]:
        """
        Find all implementation implementations whose names
        contain the given substring (case-insensitive).

        :param needle: Substring to search for.
        :type needle: str

        :return: List of matching implementation classes.
        :rtype: list[Type[ImplementationType]]
        """
        n = needle.lower()
        return [
            impl for key, impl in cls._registry.items() if n in key.lower()
        ]

    @classmethod
    def find_regex(cls, pattern: str) -> list[Type[ImplementationType]]:
        """
        Find all implementation implementations whose names
        match the given regex pattern (case-insensitive).

        :param pattern: Regex pattern to search for.
        :type pattern: str

        :return: List of matching implementation classes.
        :rtype: list[Type[ImplementationType]]
        """
        rx = re.compile(pattern, re.IGNORECASE)
        return [impl for key, impl in cls._registry.items() if rx.search(key)]

    @classmethod
    def instantiate(cls, name: str, *args, **kwargs) -> ImplementationType:
        """
        Instantiate an implementation implementation by name.

        :param name: Name of the implementation to instantiate.
        :type name: str

        :return: Instance of the implementation.
        :rtype: ImplementationType
        """
        impl = cls.get(name)
        return impl(*args, **kwargs)  # type: ignore[call-arg]

    @classmethod
    def clear(cls):
        """
        Clear all registered implementation implementations.
        """
        with cls._lock:
            cls._registry.clear()

    @classmethod
    def __iter__(cls) -> Iterator[tuple[str, Type[ImplementationType]]]:
        return iter(cls._registry.items())

    @classmethod
    def __len__(cls) -> int:
        return len(cls._registry)
