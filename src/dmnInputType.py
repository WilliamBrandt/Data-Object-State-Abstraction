from enum import Enum

class DMNInputType(Enum):
    state = "state"
    attribute = "attribute"
    relation = "relation"
    history = "history"