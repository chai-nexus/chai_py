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

### Testing

Tests can be run using [pytest](http://pytest.org/).

    $ python -m pytest

## Configuration

You must authenticate using your developer id and key before various
operations are possible.


```python
from chai_py.auth import set_auth
set_auth('my_developer_uid', 'my_developer_key')
```

## Examples

### Query for a deployed chatbots

You can request details of a deployed bot using the bot uid

```
from chai_py import bots
bot = bots.get_bot('_bot_id')
```

for example to check of whether the bot can be seen on the app
by other users (it has an "active" status).

You can also query for all the bots deployed by a given user.

```
from chai_py import bots
my_bots = bots.get_developer_bots('my_developer_id')
```

This is a good way to remind yourself of the bots you have deployed
in the past and their bot ids.

## Colab Notebook

Alternatively, check out the [notebook](https://colab.research.google.com/drive/1YB6mQkcmisEBIHOjvGnWi0z9lLiaRNT5)! 

## Requirements

Python 3.7 is required due to the usage of `dataclasses`.

Manual workarounds exist (see [here](https://stackoverflow.com/q/1868714)), enabling the potential support of earlier 
versions of Python. Other potential limiting factors include the use of `asyncio.run()`, and of `async` in general.

## Get Involved

Come join us on [Discord](https://discord.gg/YfrVwBtYWb)!
