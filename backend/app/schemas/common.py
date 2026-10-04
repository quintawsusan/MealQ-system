from enum import Enum
class UserRole(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    STUDENT = "STUDENT"
    
class MealSessionStatus(str, Enum):
    SCHEDULED = "SCHEDULED"; ACTIVE = "ACTIVE"; PAUSED = "PAUSED"; COMPLETED = "COMPLETED"
    
class BatchStatus(str, Enum):
    WAITING = "WAITING"; CALLED = "CALLED"; COMPLETED = "COMPLETED"
    
class MealResponseValue(str, Enum):
    GOING = "GOING"; SKIPPED = "SKIPPED"; NO_RESPONSE = "NO_RESPONSE"
