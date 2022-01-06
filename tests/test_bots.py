import mock

from chai_py import bots


@mock.patch('requests.get')
def test_get_deployed_bot(get):
    raw_response = {'data': {
        'name': 'Eliza',
        'bot_uid': '_bot_test123',
        'developer_uid': 'dev_123',
        'status': 'inactive'
    }}

    get.return_value = mock.Mock(
        status_code=200,
        json=mock.Mock(return_value=raw_response)
    )

    expected = bots.DeployedBot(
        '_bot_test123',
        'Eliza',
        'dev_123',
        bots.BotStatus.INACTIVE
    )

    bot = bots.get_deployed_bot('_bot_test123')
    assert bot == expected


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
        bots.DeployedBot('_bot_test123', 'Eliza', 'dev_123', bots.BotStatus.INACTIVE),
        bots.DeployedBot('_bot_test999', 'Daisy', 'dev_123', bots.BotStatus.ACTIVE)
    ]

    bot = bots.get_developer_bots('dev_123')
    assert bot == expected
