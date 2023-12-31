from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models


# USER 생성 매니저
class UserManager(BaseUserManager):
    def create_user(self, username, email, fullname, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(
            username=username, email=email, fullname=fullname, **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, username, email, fullname, password=None, **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(username, email, fullname, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=20, unique=True, db_index=True)  # index 생성
    fullname = models.CharField(max_length=10, null=False)
    email = models.EmailField(verbose_name="email", max_length=100, null=False)
    is_active = models.BooleanField(default=False)  # Email 인증 완료시 is_active = True
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "fullname"]

    objects = UserManager()

    def __str__(self):
        return self.username
