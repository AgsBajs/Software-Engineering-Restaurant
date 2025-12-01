from enum import Enum

class Role(str, Enum):
    CUSTOMER = "customer"
    STAFF = "staff"
    ADMIN = "admin"