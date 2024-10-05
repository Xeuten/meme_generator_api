from django.contrib.auth.base_user import BaseUserManager
from django.db import IntegrityError
from django.db.models import Manager

from core.exceptions import BadRequestError, NotFoundError


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


class MemeManager(Manager):
    def all(self):
        return super().select_related("created_by", "template").all()

    def get_meme_or_404(self, meme_id: int, perform_joins: bool = False):
        queryset = self.all() if perform_joins else super().all()
        if not (meme := queryset.filter(id=meme_id).first()):
            raise NotFoundError()
        return meme


class MemeTemplateManager(Manager):
    def get_template_or_404(self, template_id: int):
        if not (template := self.all().filter(id=template_id).first()):
            raise NotFoundError()
        return template
