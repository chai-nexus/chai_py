from dataclasses import dataclass
from enum import auto, Enum


@dataclass
class LatestMessage:
    text: str
    timestamp: int  # Milliseconds since epoch


@dataclass
class Update:
    conversation_id: str
    latest_message: LatestMessage


class MessageKind(Enum):
    TEXT = auto()
    IMAGE = auto()


@dataclass
class Message:
    sender_uid: str
    timestamp: int
    message_kind: MessageKind
    content: str


class BotStatus(Enum):
    ACTIVE = 1
    INACTIVE = 2


@dataclass
class DeployedBot:
    bot_uid: str
    name: str
    developer_uid: str
    status: BotStatus

    @classmethod
    def from_json(cls, js):
        status = BotStatus[js['status'].upper()]
        return cls(js['bot_uid'], js['name'], js['developer_uid'], status)
