from django.urls import path

from . import views

app_name = "market"
urlpatterns = [
	path("load_weapons", views.load_weapons, name="load weapons"),
]
