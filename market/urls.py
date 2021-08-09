from django.urls import path

from . import views

app_name = "market"
urlpatterns = [
	path("load_weapons", views.load_weapons, name="load weapons"),
	path('weapons_bsc', views.weapons_bsc, name="weapons bsc"),
	path('update_price', views.update_price, name="update price"),
]
