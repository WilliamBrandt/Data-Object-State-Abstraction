from enum import Enum

class DMNInputType(Enum):
    state = "state"
    attribute = "attribute"
    link = "link"
    history = "history"