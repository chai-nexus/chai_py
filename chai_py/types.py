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
