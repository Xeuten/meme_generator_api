from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api.views import (
    ListTemplatesView,
    MemesView,
    MemeView,
    RandomMemeView,
    RateMemeView,
    RegisterView,
    TopMemesView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("token/", TokenObtainPairView.as_view(), name="obtain_token_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("templates/", ListTemplatesView.as_view(), name="list_templates"),
    path("memes/", MemesView.as_view(), name="list_memes"),
    path("memes/<int:id>/", MemeView.as_view(), name="meme"),
    path("memes/<int:id>/rate/", RateMemeView.as_view(), name="rate_meme"),
    path("memes/random/", RandomMemeView.as_view(), name="random_meme"),
    path("memes/top/", TopMemesView.as_view(), name="top_memes"),
]
