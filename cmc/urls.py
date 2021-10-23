from django.urls import path

from . import views

app_name = 'cmc'
urlpatterns = [
	path('ler_cmc', views.ler_cmc),
]
