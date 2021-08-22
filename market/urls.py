from django.urls import path

from . import views

app_name = 'market'
urlpatterns = [
	path('update_experience_table', views.update_experience_table),
	path('transfer_character', views.transfer_character),
	path('transfer_weapon', views.transfer_weapon),
	path('update_items_account', views.update_items_account),
	path('do_fights', views.do_fights),
	path('from_game_to_stake', views.from_game_to_stake),
	path('read_market_chars', views.read_market_chars),
	path('read_market_weapons', views.read_market_weapons),
	path('clean_weapons', views.clean_weapons),
	path('clean_chars', views.clean_chars),
	path('purchase_weapon', views.purchase_weapon),
	path('load_weapons', views.load_weapons),
]
