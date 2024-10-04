from rest_framework.fields import CharField, EmailField
from rest_framework.serializers import ModelSerializer, Serializer
from typing_extensions import Any

from api.models import MemeTemplate
from core.exceptions import BadRequestError


class RegisterSerializer(Serializer):
    email = EmailField()
    password_1 = CharField()
    password_2 = CharField()

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if attrs["password_1"] != attrs["password_2"]:
            raise BadRequestError()

        return attrs


class MemeTemplateSerializer(ModelSerializer):
    class Meta:
        model = MemeTemplate
        fields = "__all__"
