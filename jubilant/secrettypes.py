"""Dataclasses that contain parsed output from juju secrets."""

from __future__ import annotations

import dataclasses
import datetime
import enum
from typing import Any


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

@dataclasses.dataclass(frozen=True)
class Secret:
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
    revisions: list[Revision] | None
    access: list[Access] | None

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> Secret:
        return cls(
            uri=SecretURI('secret:' + d.get('uri', '')),
            name=d.get('name'),
            label=d.get('label'),
            owner=d.get('owner', ''),
            rotates=datetime.datetime.fromisoformat(d['rotates'].replace('Z', '+00:00'))
            if 'rotates' in d
            else None,
            rotation=d.get('rotation'),
            revision=d.get('revision', 1),
            description=d.get('description', ''),
            created=datetime.datetime.fromisoformat(d['created'].replace('Z', '+00:00')),
            updated=datetime.datetime.fromisoformat(d['updated'].replace('Z', '+00:00')),
            checksum=d.get('checksum'),
            expires=d.get('expires'),
            access=[Access._from_dict(access) for access in d.get('access', [])]
            if 'access' in d
            else None,
            revisions=[Revision._from_dict(revision) for revision in d.get('revisions', [])]
            if 'revisions' in d
            else None,
        )

@dataclasses.dataclass(frozen=True)
class RevealedSecret(Secret):
    """Represents a secret that was revealed, which has a content field that's populated."""
    content: dict[str, str]

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> RevealedSecret:
        content: dict[str, str] = d.get('content', {}).get('Data', {})
        secret = super()._from_dict(d)
        return cls(
            content=content,
            **dataclasses.asdict(secret)
        )


@dataclasses.dataclass(frozen=True)
class Revision:
    """Represents a revision of a secret."""

    revision: int
    backend: str
    created: datetime.datetime
    updated: datetime.datetime

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> Revision:
        return cls(
            revision=d['revision'],
            backend=d['backend'],
            created=datetime.datetime.fromisoformat(d['created'].replace('Z', '+00:00')),
            updated=datetime.datetime.fromisoformat(d['updated'].replace('Z', '+00:00')),
        )


@dataclasses.dataclass(frozen=True)
class Access:
    """Represents access to a secret."""

    target: str
    scope: AccessScope
    role: AccessRole

    @classmethod
    def _from_dict(cls, d: dict[str, Any]) -> Access:
        return cls(
            target=d['target'],
            scope=AccessScope(d['scope']),
            role=AccessRole(d['role']),
        )
