from django.contrib.auth.models import User
from django.db.models import (
    CASCADE,
    CharField,
    DateTimeField,
    IntegerChoices,
    IntegerField,
    Model,
    URLField,
)
from django.db.models.fields.related import ForeignKey


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


class MemeTemplate(Model):
    name = CharField("Name", max_length=100)
    image_url = URLField("Image URL")
    default_top_text = CharField(max_length=100, blank=True)
    default_bottom_text = CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = "Meme template"
        verbose_name_plural = "Meme templates"


class Meme(TimeStampedModel):
    template = ForeignKey(MemeTemplate, verbose_name="Template", on_delete=CASCADE)
    top_text = CharField("Top text", max_length=100)
    bottom_text = CharField("Bottom text", max_length=100)
    created_by = ForeignKey(User, verbose_name="Created by", on_delete=CASCADE)

    class Meta:
        verbose_name = "Meme"
        verbose_name_plural = "Memes"


class Rating(TimeStampedModel):
    meme = ForeignKey(
        Meme, verbose_name="Meme", on_delete=CASCADE, related_name="ratings"
    )
    user = ForeignKey(
        User, verbose_name="User", on_delete=CASCADE, related_name="ratings"
    )
    score = IntegerField("Score", choices=Score)

    class Meta:
        verbose_name = "Rating"
        verbose_name_plural = "Ratings"
        unique_together = ("meme", "user")
