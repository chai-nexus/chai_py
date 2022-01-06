from chai_py import types, bots


def test_get_deployed_bot_from_response():
    raw_api_response = {
        'name': 'Eliza',
        'bot_uid': '_bot_test123',
        'developer_uid': 'dev_123',
        'status': 'inactive'
    }

    bot = types.DeployedBot.from_json(raw_api_response)

    expected = types.DeployedBot(
        '_bot_test123',
        'Eliza',
        'dev_123',
        types.BotStatus.INACTIVE
    )

    assert bot == expected
