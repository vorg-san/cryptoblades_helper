from django.urls import path

from . import views

app_name = "market"
urlpatterns = [
	path("do_fights", views.do_fights),
	path("load_weapons", views.load_weapons),
	path("clean_weapons", views.clean_weapons),
	path('weapons_bsc', views.weapons_bsc),
	path('update_price', views.update_price),
]
