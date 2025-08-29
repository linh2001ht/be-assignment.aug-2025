import enum

class Role(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"

class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in-progress"
    DONE = "done"

class Priority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"