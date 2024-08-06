import enum


class Status(str, enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN PROGRESS"
    BLOCKED = "BLOCKED"
    DONE = "DONE"