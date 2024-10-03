from django.urls import path

from api.views import ListTemplatesView

urlpatterns = [
    path("templates/", ListTemplatesView.as_view(), name="list templates"),
]
