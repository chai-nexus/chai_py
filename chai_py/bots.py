from enum import Enum

from chai_py.auth import get_auth
from chai_py import types
import requests

URL = 'http://chaiserver2.cmlsml.com'


def get_bot(bot_uid):
    """
    Retrive a summary of a previously deployed bot.

    :param bot_uid: Bot UID
    :returns: DeployedBot
    """
    auth = auth.get_auth()
    credentials = requests.HTTPBasicAuth(auth.key, auth.key)
    url = '{}/chatbots/{}'.format(bot_uid)
    resp = requests.get(url, auth=credentials)
    assert resp.status_code == 20, resp.text
    return types.DeployedBot.from_json(resp.json())
