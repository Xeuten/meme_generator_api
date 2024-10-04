from django.contrib.auth.base_user import BaseUserManager
from django.db import IntegrityError

from core.exceptions import BadRequestError


class UserManager(BaseUserManager):
    def create_user(self, email: str, password: str, **extra_fields):
        email = self.normalize_email(email)
        model = self.model
        user = model(email=email, **extra_fields)
        user.set_password(password)
        try:
            user.save()
        except IntegrityError:
            raise BadRequestError()

        return user

    def create_superuser(self, email: str, password: str, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)
