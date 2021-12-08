from django.urls import path

from . import views

app_name = 'cmc'
urlpatterns = [
	path('good_ones', views.good_ones),
]
