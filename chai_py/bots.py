from enum import Enum

from chai_py.auth import get_auth
from chai_py import types, defaults
import requests


def get_bot(bot_uid: str):
    """
    Retrive a summary of a previously deployed bot.

    :param bot_uid: Bot UID
    :returns: DeployedBot
    """
    auth = get_auth()
    credentials = requests.auth.HTTPBasicAuth(auth.uid, auth.key)
    url = '{}/chatbots/{}'.format(defaults.API_HOST, bot_uid)
    resp = requests.get(url, auth=credentials)
    assert resp.status_code == 200, resp.text
    return types.DeployedBot.from_json(resp.json()['data'])
