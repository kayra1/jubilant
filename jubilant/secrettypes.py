"""Dataclasses that contain parsed output from juju secrets."""

from __future__ import annotations

import dataclasses
import datetime
from typing import Dict, Generic, Literal, TypedDict, TypeVar

from typing_extensions import NotRequired


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


@dataclasses.dataclass
class SecretAccess:
    """Represents access to a secret."""

    target: str
    scope: str
    role: str


@dataclasses.dataclass
class SecretRevision:
    """Represents a revision of a secret."""

    revision: int
    backend: str
    created: datetime.datetime
    updated: datetime.datetime


NoneType = type(None)
Hidden = NoneType
Revealed = Dict[str, str]
T = TypeVar('T', Revealed, Hidden)


@dataclasses.dataclass
class Secret(Generic[T]):
    """Represents a secret."""

    uri: SecretURI
    revision: int
    checksum: str
    expires: str | None
    rotation: str | Literal['never']
    rotates: str | None
    owner: str | None
    description: str | None
    name: str | None
    label: str | None
    created: datetime.datetime
    updated: datetime.datetime
    error: str
    content: T
    revisions: list[SecretRevision]
    access: list[SecretAccess]


class SecretResponse(TypedDict, total=False):
    """TypedDict for secret response that arrives from the juju CLI."""

    uri: SecretURI
    revision: int
    checksum: str
    expires: str
    rotation: str
    rotates: str
    owner: str
    description: str
    name: str
    label: str
    created: str
    updated: str
    error: str
    content: NotRequired[dict[str, dict[str, str]]]
    revisions: list[SecretRevisionResponse]
    access: list[SecretAccess]


class SecretRevisionResponse(TypedDict):
    """TypedDict for revision response that arrives from the juju CLI."""

    revision: int
    backend: str
    created: str
    updated: str
