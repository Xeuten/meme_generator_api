from rest_framework.fields import (
    CharField,
    ChoiceField,
    DecimalField,
    EmailField,
    IntegerField,
    URLField,
)
from rest_framework.serializers import ModelSerializer, Serializer
from typing_extensions import Any

from api.models import Meme, MemeTemplate, Score, User
from core.exceptions import BadRequestError


class RegisterSerializer(Serializer):
    email = EmailField()
    password_1 = CharField()
    password_2 = CharField()

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if attrs["password_1"] != attrs["password_2"]:
            raise BadRequestError()

        return attrs


class ShortUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
        )


class MemeTemplateSerializer(ModelSerializer):
    class Meta:
        model = MemeTemplate
        fields = "__all__"


class MemeSerializer(ModelSerializer):
    template = MemeTemplateSerializer()
    created_by = ShortUserSerializer()

    class Meta:
        model = Meme
        fields = "__all__"


class RatedMemeSerializer(ModelSerializer):
    template = MemeTemplateSerializer()
    created_by = ShortUserSerializer()
    average_score = DecimalField(max_digits=3, decimal_places=2)

    class Meta:
        model = Meme
        fields = ("template", "top_text", "bottom_text", "created_by", "average_score")


class ShortMemeSerializer(ModelSerializer):
    class Meta:
        model = Meme
        fields = "__all__"


class CreateMemeSerializer(Serializer):
    template_id = IntegerField()
    top_text = CharField(required=False)
    bottom_text = CharField(required=False)


class RateMemeSerializer(Serializer):
    score = ChoiceField(choices=Score)


class SurpriseMemeSerializer(Serializer):
    url = URLField()
