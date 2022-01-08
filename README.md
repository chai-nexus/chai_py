# ChaiPy

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/chaipy)
![PyPI](https://img.shields.io/pypi/v/chaipy)

A developer interface for creating Chat AIs for the Chai app.

## Install

You can install chai_py using pip

    $ pip install -U chai_py

## Local development

A quick start guide is available [here](https://chai.ml/docs/), with a minimal example available on GitHub 
[here](https://github.com/chai-nexus/chai_py_quickstart).

## Configuration

You must authenticate using your developer id and key before various
operations are possible.

```python
from chai_py.auth import set_auth
set_auth('my_developer_uid', 'my_developer_key')
```

You can create a key through the [Chai website](https://chai.ml/dev)

## Examples

### Deploying a bot

Once you have a bot ready to deploy you can package it

```python
from chai_py import package, Metadata

package(
    Metadata(
        name='My Bot Name',
	image_url='http://url_of_image.jpg',
	color='f1abab',
	developer_uid='my_developer_uid',
	description='Talk to my example bot',
	input_class=MyBotClass
    )
    requirements=['retry']
)

```

which will create a file `_package.zip` which can be uploaded. To upload it

```python
from chai_py import upload_and_deploy
bot_uid = upload_and_deploy('_package.zip')
wait_for_deployment(bot_uid)
```

and finally you can get a link or QR code for your deployed bot using

```python
from chai_py.deployment import advertise_deployed_bot
advertise_deployed_bot(bot_uid)
```

which you can use to talk to you bot or share with friends.

### Get a list of all the chatbots you have deployed

You can also query for all the bots you have deployed.

```python
from chai_py import deployed
my_bots = deployed.get_bots()
```

This is a good way to remind yourself of the bots you have deployed
in the past, their bot identifier and whether they are visable to other users
(their status is "active").

### Get the debug logs of a deployed chatbot

If you bot is failing to respond it may be that it has an error.  You
can retrieve the logs in order to investigate further

```python
from chai_py import cloud_logs
logs = cloud_logs.get_logs(bot_uid)
cloud_logs.display_logs(logs)
```

### Make a bot visible to the public

By default a bot is inactive, it can be viewed and shared via a link or QR code
but will not be discoverable by users of the app.

To make an app visible run

```python
from chai_py import deployed
deployed.activate_bot(bot_uid)
```

and to make a bot not discoverable run

```python
from chai_py import deployed
deployed.deactivate_bot(bot_uid)
```

Permission to make a chatbot discoverable requires your developer ID to
be whitelisted. Speak to us over WhatsApp and we can grant you permission.

## Testing

Tests can be run using [pytest](http://pytest.org/).

    $ python -m pytest


## Requirements

Python 3.7 is required due to the usage of `dataclasses`.

Manual workarounds exist (see [here](https://stackoverflow.com/q/1868714)), enabling the potential support of earlier 
versions of Python. Other potential limiting factors include the use of `asyncio.run()`, and of `async` in general.

## Get Involved

Speak to us on [Whatsapp](https://chat.whatsapp.com/GvdhL4f3304FxcAxZEbpi4)

Come join us on [Discord](https://discord.gg/YfrVwBtYWb)!
