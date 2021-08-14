from django.urls import path

from . import views

app_name = "market"
urlpatterns = [
	path("do_fights", views.do_fights),
	path('read_market_chars', views.read_market_chars),
	path('read_market_weapons', views.read_market_weapons),
	path("clean_weapons", views.clean_weapons),
	path("clean_chars", views.clean_chars),
	path('purchase_weapon', views.purchase_weapon),
	path("load_weapons", views.load_weapons),
]
