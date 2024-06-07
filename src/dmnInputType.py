from enum import Enum

class DMNInputType(Enum):
    state = "state"
    object = "object"
    relation = "relation"
    history = "history"