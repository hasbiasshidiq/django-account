from django.db import models
import enum
from django.utils import timezone

# Create your models here.

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class AccountRoleEnum(enum.Enum):
    operator = "operator"
    supervisor = "supervisor"
    super_admin = "super_admin"

    def translate(self):
        # Split the enum value by underscores
        words = self.value.split("_")
        # Capitalize each word and join them with a space
        return " ".join(word.capitalize() for word in words)


class AccountStatusEnum(enum.Enum):
    active = "active"
    inactive = "inactive"
    send_invitation = "send_invitation"
    invitation_expired = "invitation_expired"

    def translate(self):
        # Split the enum value by underscores
        words = self.value.split("_")
        # Capitalize each word and join them with a space
        return " ".join(word.capitalize() for word in words)


class Account(AbstractBaseUser):
    ROLE_CHOICES = [(role.value, role.translate()) for role in AccountRoleEnum]
    STATUS_CHOICES = [(role.value, role.translate()) for role in AccountStatusEnum]

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=tuple(ROLE_CHOICES))
    status = models.CharField(max_length=20, choices=tuple(STATUS_CHOICES))
    has_set_password = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "role", "status"]

    objects = BaseUserManager()

    class Meta:
        ordering = ["id"]
        db_table = "account"


class AccountEmailTokenStatusEnum(enum.Enum):
    active = "active"
    inactive = "inactive"

    def translate(self):
        # Split the enum value by underscores
        words = self.value.split("_")
        # Capitalize each word and join them with a space
        return " ".join(word.capitalize() for word in words)


class AccountEmailToken(models.Model):

    STATUS_CHOICES = [
        (role.value, role.translate()) for role in AccountEmailTokenStatusEnum
    ]

    id = models.BigAutoField(primary_key=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=tuple(STATUS_CHOICES))
    token = models.UUIDField()
    expired_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]
        db_table = "account_email_token"
