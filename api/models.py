from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db.models import (
    CASCADE,
    BooleanField,
    CharField,
    DateTimeField,
    EmailField,
    ImageField,
    IntegerField,
    Model,
    URLField,
)
from django.db.models.fields.related import ForeignKey
from django.utils.translation import gettext_lazy as _

from api.enums import Score
from api.managers import MemeManager, MemeTemplateManager, UserManager


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

    # This field is used to store the image of the meme. In a real-world application,
    # we would store the image in a cloud storage service like AWS S3, and store the
    # URL of the image in the database.
    image = ImageField(_("Image"), upload_to="memes/", blank=True, null=True)

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
