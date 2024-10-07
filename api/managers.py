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
    def all_with_joins(self):
        """
        This method is used to perform joins with the created_by and template tables,
        which is useful when we want to return the created_by and template information
        without making additional queries.
        """
        return self.select_related("created_by", "template").all()

    def get_meme_with_joins_or_404(self, meme_id: int):
        if not (meme := self.all_with_joins().filter(id=meme_id).first()):
            raise NotFoundError()
        return meme

    def get_meme_or_404(self, meme_id: int):
        if not (meme := self.filter(id=meme_id).first()):
            raise NotFoundError()
        return meme

    def get_random_meme(self):
        """
        This method is used to get a random meme from the database in efficient way.
        It uses a feature that is available in PostgreSQL, which is the TABLESAMPLE
        clause. The clause is used to get a random sample of the table, which is
        useful when we want to get a random row from a large table. If the table is
        small, we use regular random ordering.
        """
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
        """
        This method is used to get the top 10 memes based on the average score of their
        ratings. We annotate the queryset with the average score of the ratings and
        then order the queryset by the average score in descending order.
        """
        return (
            self.all_with_joins()
            .annotate(
                average_score=Coalesce(
                    Avg("ratings__score"), Value(0), output_field=FloatField()
                )
            )
            .order_by("-average_score")[:10]
        )


class MemeTemplateManager(Manager):
    def get_template_or_404(self, template_id: int):
        if not (template := self.filter(id=template_id).first()):
            raise NotFoundError()
        return template

    def get_random_order_templates(self):
        return self.all().order_by("?")
