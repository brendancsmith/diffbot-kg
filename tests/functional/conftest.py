import logging
import os

import dotenv
import pytest

ORG_NAME = "Diffbot"
ORG_ENTITY_ID = "EYX1i02YVPsuT7fPLUYgRhQ"
ORG_URL = "www.diffbot.com"

ORG2_NAME = "Apple"
ORG2_ENTITY_ID = "EHb0_0NEcMwyY8b083taTTw"
ORG2_URL = "www.apple.com"


class Secret:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "Secret(********)"

    def __str___(self):
        return "*******"


@pytest.fixture(scope="session", autouse=True)
def token():
    __tracebackhide__ = True
    dotenv.load_dotenv(override=True)
    return Secret(os.environ.get("DIFFBOT_TOKEN"))


@pytest.fixture(scope="session", autouse=True)
def suppress_aiohttp_output():
    log = logging.getLogger("aiohttp")
    log.setLevel(logging.CRITICAL + 1)
