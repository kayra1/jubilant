import datetime
import json

import jubilant


def test_add_secret(juju: jubilant.Juju):
    uri = juju.secret('sec1', {'username': 'usr', 'password': 'hunter2'}, info='A description.')

    output = juju.cli('show-secret', 'sec1', '--reveal', '--format', 'json')
    result = json.loads(output)
    secret = result[uri.unique_identifier]
    assert secret['name'] == 'sec1'
    assert secret['description'] == 'A description.'
    assert secret['content']['Data'] == {'username': 'usr', 'password': 'hunter2'}


def test_update_secret(juju: jubilant.Juju):
    uri = juju.secret('sec1', {'username': 'usr', 'password': 'hunter2'}, info='A description.')
    uri2 = juju.secret(
        'sec1', {'username': 'usr', 'password': 'hunter3'}, info='A new description.'
    )

    assert uri == uri2
    output = juju.cli('show-secret', 'sec1', '--reveal', '--format', 'json')
    result = json.loads(output)
    secret = result[uri.unique_identifier]
    assert secret['name'] == 'sec1'
    assert secret['description'] == 'A new description.'
    assert secret['content']['Data'] == {'username': 'usr', 'password': 'hunter3'}


def test_get_all_secrets(juju: jubilant.Juju):
    uris: list[str] = []
    args = [
        {'label': 'sec1', 'username': 'usr', 'password': 'hunter2', 'info': 'A description'},
        {'label': 'sec2', 'username': 'usr2', 'password': 'hunter3', 'info': 'A new description'},
    ]
    for arg in args:
        uri = juju.secret(
            arg['label'],
            {'username': arg['username'], 'password': arg['password']},
            info=arg['info'],
        )
        uris.append(uri)
    secrets = juju.secret()

    assert isinstance(secrets, list)
    assert len(secrets) > 0
    for secret in secrets:
        assert secret.uri in uris
        assert secret.revision == 1
        assert secret.name == '<model>'
        assert secret.description in [arg['info'] for arg in args]
        assert secret.created.year == datetime.datetime.now().year
        assert secret.created == secret.updated


def test_get_secret(juju: jubilant.Juju):
    uri = juju.secret('sec1', {'username': 'usr', 'password': 'hunter2'}, info='A description.')

    secret = juju.secret(label='sec1')
    secret2 = juju.secret(uri=uri)

    assert secret == secret2
    assert secret.uri == uri
    assert secret.revision == 1
    assert secret.owner == '<model>'
    assert secret.name == 'sec1'
    assert secret.description == 'A description'
    assert secret.created.year == datetime.datetime.now().year
    assert secret.created == secret.updated
    assert secret.content == {'username': 'usr', 'password': 'hunter2'}
