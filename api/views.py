from rest_framework import status
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.dto import MemeDTO
from api.models import Meme, MemeTemplate
from api.serializers import (
    CreateMemeSerializer,
    MemeSerializer,
    MemeTemplateSerializer,
    RegisterSerializer,
)
from api.services import CreateMemeService, RegisterService


class RegisterView(GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        RegisterService(
            serializer.validated_data["email"], serializer.validated_data["password_1"]
        ).execute()
        return Response(status=status.HTTP_201_CREATED)


class ListTemplatesView(ListAPIView):
    serializer_class = MemeTemplateSerializer
    queryset = MemeTemplate.objects.all()


class MemesView(ListAPIView):
    serializer_class = MemeSerializer
    queryset = Meme.objects.all()
    pagination_class = PageNumberPagination

    def post(self, request, *args, **kwargs):
        serializer = CreateMemeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        meme_id = CreateMemeService(
            MemeDTO(created_by_id=request.user.id, **serializer.validated_data)
        ).execute()
        return Response(data={"id": meme_id}, status=status.HTTP_201_CREATED)
