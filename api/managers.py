from django.contrib.auth.base_user import BaseUserManager
from django.db import IntegrityError
from django.db.models import Avg, FloatField, Manager, Value
from django.db.models.functions.comparison import Coalesce

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

    def get_random_meme(self):
        table = self.model._meta.db_table
        large_table_query = f"SELECT * FROM {table} TABLESAMPLE SYSTEM (1) LIMIT 1"
        try:
            return self.raw(
                f"""
                    (
                        {large_table_query}
                    )
                    UNION ALL
                    (
                        SELECT * FROM {table}
                        WHERE NOT EXISTS ({large_table_query})
                        ORDER BY RANDOM()
                        LIMIT 1
                    )
                    LIMIT 1
                """
            )[0]
        except IndexError:
            raise NotFoundError()

    def get_top_memes(self):
        return (
            self.all()
            .annotate(
                average_score=Coalesce(
                    Avg("ratings__score"), Value(0), output_field=FloatField()
                )
            )
            .order_by("-average_score")[:10]
        )


class MemeTemplateManager(Manager):
    def get_template_or_404(self, template_id: int):
        if not (template := self.all().filter(id=template_id).first()):
            raise NotFoundError()
        return template

    def get_random_order_templates(self):
        return self.all().order_by("?")
