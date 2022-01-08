import mock
import pytest
import requests

from chai_py import deployed as dep
from chai_py import defaults


@pytest.fixture(autouse=True)
def set_authentication():
    with mock.patch('chai_py.auth.get_auth') as m:
        m.uid = 'test_uid'
        m.key = 'test_key'
        yield


@mock.patch('requests.get')
def test_get_developer_bots(get):
    raw_response = {'data': [
        {
            'name': 'Eliza', 'bot_uid': '_bot_test123',
            'developer_uid': 'dev_123', 'status': 'inactive'
        },
        {
            'name': 'Daisy', 'bot_uid': '_bot_test999',
            'developer_uid': 'dev_123', 'status': 'active'
        },
    ]}

    get.return_value = mock.Mock(
        status_code=200,
        json=mock.Mock(return_value=raw_response)
    )

    expected = [
        dep.DeployedBot('_bot_test123', 'Eliza', 'dev_123', dep.BotStatus.INACTIVE),
        dep.DeployedBot('_bot_test999', 'Daisy', 'dev_123', dep.BotStatus.ACTIVE)
    ]

    bot = dep.get_bots()
    assert bot == expected


@mock.patch('requests.post')
def test_activate_bot(post):
    post.return_value = mock.Mock(
        status_code=200,
        json=mock.Mock(return_value={})
    )

    res = dep.activate_bot('bot_123')
    assert res == {'status': 'active'}

    post.assert_called_with(
        '{}/chatbots/bot_123'.format(defaults.API_HOST),
        json={'status': 'active'},
        auth=requests.auth.HTTPBasicAuth('test_uid', 'test_key')
    )


@mock.patch('requests.post')
def test_deactivate_bot(post):
    post.return_value = mock.Mock(
        status_code=200,
        json=mock.Mock(return_value={})
    )

    res = dep.deactivate_bot('bot_123')
    assert res == {'status': 'inactive'}

    post.assert_called_with(
        '{}/chatbots/bot_123'.format(defaults.API_HOST),
        json={'status': 'inactive'},
        auth=requests.auth.HTTPBasicAuth('test_uid', 'test_key')
    )
