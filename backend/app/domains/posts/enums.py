from enum import Enum

class TopicType(str, Enum):
    STANDARD = "STANDARD"
    EVENT = "EVENT"
    OFFER = "OFFER"
    ALERT = "ALERT"

class PostState(str, Enum):
    UNSPECIFIED = "LOCAL_POST_STATE_UNSPECIFIED"
    REJECTED = "REJECTED"
    LIVE = "LIVE"
    PROCESSING = "PROCESSING"

class ActionType(str, Enum):
    BOOK = "BOOK"
    ORDER = "ORDER"
    SHOP = "SHOP"
    LEARN_MORE = "LEARN_MORE"
    SIGN_UP = "SIGN_UP"
    CALL = "CALL"

class AlertType(str, Enum):
    COVID_19 = "COVID_19"
