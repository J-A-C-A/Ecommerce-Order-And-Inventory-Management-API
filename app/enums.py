import enum

class OrderStatus(str, enum.Enum):
    PENDING = "Pending"
    PAID = "Paid"
    SHIPPED = "Shipped"
    DELIVERED = "Delivered"
    CANCELED = "Canceled"

class RoleType(str, enum.Enum):
    CUSTOMER = "Customer"
    ADMIN = "Admin"

class ChangeAuthor(str, enum.Enum):
    SYSTEM = "System"
    ADMIN = "Admin"
