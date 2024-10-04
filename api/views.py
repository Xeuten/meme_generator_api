from rest_framework import status
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.models import MemeTemplate
from api.serializers import MemeTemplateSerializer, RegisterSerializer
from api.services import RegisterService


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
