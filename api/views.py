from rest_framework import status
from rest_framework.generics import GenericAPIView, ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.dto import MemeDTO, RateMemeDTO
from api.models import Meme, MemeTemplate
from api.serializers import (
    CreateMemeSerializer,
    MemeSerializer,
    MemeTemplateSerializer,
    RateMemeSerializer,
    RegisterSerializer,
)
from api.services import (
    CreateMemeService,
    MemeService,
    RateMemeService,
    RegisterService,
)


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
        return Response(data={"meme_id": meme_id}, status=status.HTTP_201_CREATED)


class MemeView(RetrieveAPIView):
    serializer_class = MemeSerializer

    def get_object(self):
        return MemeService(self.kwargs["id"]).execute()


class RateMemeView(GenericAPIView):
    serializer_class = RateMemeSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        rating_id = RateMemeService(
            RateMemeDTO(
                meme_id=kwargs["id"],
                user_id=request.user.id,
                **serializer.validated_data
            )
        ).execute()
        return Response(data={"rating_id": rating_id}, status=status.HTTP_201_CREATED)
