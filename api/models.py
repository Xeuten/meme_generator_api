from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db.models import (
    CASCADE,
    BooleanField,
    CharField,
    DateTimeField,
    EmailField,
    IntegerChoices,
    IntegerField,
    Model,
    URLField,
)
from django.db.models.fields.related import ForeignKey
from django.utils.translation import gettext_lazy as _

from api.managers import MemeManager, MemeTemplateManager, UserManager


class Score(IntegerChoices):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5


class TimeStampedModel(Model):
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class User(AbstractBaseUser, PermissionsMixin):
    email = EmailField(verbose_name=_("Email"), unique=True)
    is_staff = BooleanField(verbose_name=_("Is staff"), default=False)

    USERNAME_FIELD = "email"

    objects = UserManager()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")


class MemeTemplate(Model):
    name = CharField(_("Name"), max_length=100)
    image_url = URLField(_("Image URL"))
    default_top_text = CharField(_("Default top text"), max_length=100, blank=True)
    default_bottom_text = CharField(
        _("Default bottom text"), max_length=100, blank=True
    )

    objects = MemeTemplateManager()

    class Meta:
        verbose_name = _("Meme template")
        verbose_name_plural = _("Meme templates")


class Meme(TimeStampedModel):
    template = ForeignKey(MemeTemplate, verbose_name=_("Template"), on_delete=CASCADE)
    top_text = CharField(_("Top text"), max_length=100)
    bottom_text = CharField(_("Bottom text"), max_length=100)
    created_by = ForeignKey(User, verbose_name=_("Created by"), on_delete=CASCADE)

    objects = MemeManager()

    class Meta:
        verbose_name = _("Meme")
        verbose_name_plural = _("Memes")


class Rating(TimeStampedModel):
    meme = ForeignKey(
        Meme, verbose_name=_("Meme"), on_delete=CASCADE, related_name="ratings"
    )
    user = ForeignKey(
        User, verbose_name=_("User"), on_delete=CASCADE, related_name="ratings"
    )
    score = IntegerField(_("Score"), choices=Score)

    class Meta:
        verbose_name = _("Rating")
        verbose_name_plural = _("Ratings")
        unique_together = ("meme", "user")
