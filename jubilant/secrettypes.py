"""Dataclasses that contain parsed output from juju secrets."""

from __future__ import annotations

import dataclasses
import datetime
import enum
from typing import Dict, Generic, TypedDict, TypeVar

from typing_extensions import Required


class Rotate(enum.Enum):
    """Secret rotation policies."""

    NEVER = 'never'
    HOURLY = 'hourly'
    DAILY = 'daily'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'
    QUARTERLY = 'quarterly'
    YEARLY = 'yearly'


class AccessScope(enum.Enum):
    """Secret access scopes."""

    UNIT = 'unit'
    APP = 'application'
    MODEL = 'model'
    RELATION = 'relation'


class AccessRole(enum.Enum):
    """Secret access roles."""

    VIEW = 'view'
    ROTATE = 'rotate'
    MANAGE = 'manage'


class SecretURI(str):
    """A string subclass that represents a secret URI ("secret:...")."""

    @property
    def unique_identifier(self) -> str:
        """Unique identifier of this secret URI.

        This is the secret's globally-unique identifier (currently a 20-character Xid,
        for example "9m4e2mr0ui3e8a215n4g").
        """
        if '/' in self:
            # Handle 'secret://MODEL-UUID/UNIQUE-IDENTIFIER'
            return self.rsplit('/', maxsplit=1)[-1]
        elif self.startswith('secret:'):
            # Handle common case of 'secret:UNIQUE-IDENTIFIER'
            return self[len('secret:') :]
        else:
            return str(self)


NoneType = type(None)
Hidden = NoneType
Revealed = Dict[str, str]
T = TypeVar('T', Revealed, Hidden)


@dataclasses.dataclass(frozen=True)
class Secret(Generic[T]):
    """Represents a secret."""

    uri: SecretURI
    revision: int
    checksum: str | None
    expires: str | None
    rotation: Rotate | None
    rotates: datetime.datetime | None
    owner: str
    description: str | None
    name: str | None
    label: str | None
    created: datetime.datetime
    updated: datetime.datetime
    content: T
    revisions: list[Revision] | None
    access: list[Access] | None


@dataclasses.dataclass(frozen=True)
class Revision:
    """Represents a revision of a secret."""

    revision: int
    backend: str
    created: datetime.datetime
    updated: datetime.datetime


@dataclasses.dataclass(frozen=True)
class Access:
    """Represents access to a secret."""

    target: str
    scope: AccessScope
    role: AccessRole


class _SecretResponse(TypedDict, total=False): # pyright: ignore[reportUnusedClass]
    """TypedDict for secret response that arrives from the juju CLI."""

    uri: SecretURI
    revision: Required[int]
    checksum: str
    expires: str
    rotation: Rotate
    rotates: str
    owner: Required[str]
    description: str
    name: str
    label: str
    created: Required[str]
    updated: Required[str]
    error: str
    content: dict[str, dict[str, str]]
    revisions: list[_SecretRevisionResponse]
    access: list[_SecretAccessResponse]


class _SecretRevisionResponse(TypedDict):
    """TypedDict for revision response that arrives from the juju CLI."""

    revision: int
    backend: str
    created: str
    updated: str


class _SecretAccessResponse(TypedDict):
    """TypedDict for access response that arrives from the juju CLI."""

    target: str
    scope: str
    role: str
