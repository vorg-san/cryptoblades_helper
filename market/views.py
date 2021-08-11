from django.shortcuts import render
from django.urls import reverse
from eth_utils import address
from . import models
import requests
import json
from .serializers import WeaponSerializer 
from rest_framework import viewsets      
from django.http import HttpResponse
from time import sleep
from random import randrange
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from web3 import Web3
import time, json
# from .contract import abi_market
import os
import math

market_address = '0x90099dA42806b21128A094C713347C7885aF79e2'	
weapons_address = '0x7e091b0a220356b157131c831258a9c98ac8031a'
characters_address = '0xc6f252c2cdd4087e30608a35c022ce490b58179b'
cryptoblades_address = '0x39bea96e13453ed52a734b6aceed4c41f57b2271'
my_accounts = [
	'0x102BaC4dcf67E88C85ee8114A65b9A391153eA50',
	'0x537b677952604b163a842C7A01cf68f7ed156969',
	'0xb99fbf82D50C802C4a17aB912539D84732Eb59B7',
	'0x657efBE39eE5Ee7E5f58DDdf580ed5781ABED987',
	'0xEaD11D7D91afa4249CeE933Ca549D74C37272AC9',
	'0xB3F9b429Ba95c02b64782d45F490E33fCCC957d2'
]


web3 = Web3(Web3.HTTPProvider('https://bsc-dataseed1.defibit.io/'))

with open(os.path.dirname(__file__) + '\\contracts\\NFTMarket.json') as json_file:
    abi_market = json.load(json_file)['abi']
with open(os.path.dirname(__file__) + '\\contracts\\Weapons.json') as json_file:
    abi_weapons = json.load(json_file)['abi']
with open(os.path.dirname(__file__) + '\\contracts\\Characters.json') as json_file:
    abi_characters = json.load(json_file)['abi']
with open(os.path.dirname(__file__) + '\\contracts\\CryptoBlades.json') as json_file:
    abi_cryptoblades = json.load(json_file)['abi']

market_contract = web3.eth.contract(address=web3.toChecksumAddress(market_address), abi=abi_market)
weapons_contract = web3.eth.contract(address=web3.toChecksumAddress(weapons_address), abi=abi_weapons)
characters_contract = web3.eth.contract(address=web3.toChecksumAddress(characters_address), abi=abi_characters)
cryptoblades_contract = web3.eth.contract(address=web3.toChecksumAddress(cryptoblades_address), abi=abi_cryptoblades)

num_market_list_per_call = 3000

def get_character_power(level):
    return ((1000 + (level * 10)) * (math.floor(level / 10) + 1))

def real_stat_power(char_trait, stat_trait, value):
	return 0.25 * (math.floor(value * 1.07) if char_trait == stat_trait else math.floor(value * 1.03) if stat_trait == 4 else value)

def decode_enemy(n):
	return {
		'id' : n,
		'power': n & 0xFFFFFF, 
		'trait': n >> 24
	}

def decode_weapon(data): 
	properties = data[0]
	stats = (properties >> 5) & 0x7f
	burn_points = +data[9]
	
	return {
		'trait': (properties >> 3) & 0x3,
		'stat1_trait': stats % 5,
		'stat2_trait': (math.floor(stats / 5) % 5),
		'stat3_trait': (math.floor(math.floor(stats / 5) / 5) % 5),
		'stat1': +data[1],
		'stat2': +data[2],
		'stat3': +data[3],
		'level': +data[4],
		'burn_points': burn_points,
		'bonus_power': +data[10],
		'low_star_burn_points': burn_points & 0xff,
		'four_star_burn_points': (burn_points >> 8) & 0xff,
		'five_star_burn_points': (burn_points >> 16) & 0xff,
		'stars': (+properties) & 0x7,
	}

def decode_character(data): 
	return {
		'xp': data[0],
		'level': data[1],
		'trait': data[2],
		'staminaTimestamp': datetime.fromtimestamp(data[3])
	}

def fight(request):
	try:
		chars = cryptoblades_contract.functions.getMyCharacters().call({'from': my_accounts[2]})

		for char in chars[2:]:
			stamina = characters_contract.functions.getStaminaPoints(char).call()

			if stamina > 0: #160:
				character_data = decode_character(characters_contract.functions.get(char).call())
				character_power = get_character_power(character_data['level'])

				weapons = cryptoblades_contract.functions.getMyWeapons().call({'from': my_accounts[2]})
				enemy_options = []

				for weapon in weapons:
					weapon_data = decode_weapon(weapons_contract.functions.get(weapon).call())
					weapon_multiplier = 1 + 0.01 * (
							real_stat_power(character_data['trait'], weapon_data['stat1_trait'], weapon_data['stat1']) +
							real_stat_power(character_data['trait'], weapon_data['stat2_trait'], weapon_data['stat2']) +
							real_stat_power(character_data['trait'], weapon_data['stat3_trait'], weapon_data['stat3']) 
						)
					total_power = (character_power * weapon_multiplier) + weapon_data['bonus_power']
								
					enemies_data = [decode_enemy(e) for e in cryptoblades_contract.functions.getTargets(char, weapon).call()]

					for enemy_data in enemies_data:
						total_multiplier = 1 + (0.075 if weapon_data['trait'] == character_data['trait'] else 0) + 0.075 * (1 if (character_data['trait'] + 1) % 4 == enemy_data['trait'] else -1 if (enemy_data['trait'] + 1) % 4 == character_data['trait'] else 0)
						player_roll = [total_power * total_multiplier * 0.9, total_power * total_multiplier * 1.1]
						enemy_roll = [enemy_data['power'] * 0.9, enemy_data['power'] * 1.1]

						win = 0
						total = 0
						for i in range(math.floor(player_roll[0]), math.floor(player_roll[1]) + 1, 1):
							for j in range(math.floor(enemy_roll[0]), math.floor(enemy_roll[1]) + 1, 1):
								if i >= j:
									win += 1
								total += 1
						chance_win = win / total

						enemy_options.append({
								'weapon': weapon, 
								'enemy_id': enemy_data['id'], 
								'enemy_power': enemy_data['power'], 
								'chance_win': chance_win
							})

				enemy_options = sorted(enemy_options, key=lambda k: -k['chance_win']) 
				print(enemy_options)

				while len(enemy_options) > 2 and enemy_options[0]['chance_win'] >= 92 and enemy_options[1]['chance_win'] >= 92 and enemy_options[0]['enemy_power'] < enemy_options[1]['enemy_power']:
					print('largando', enemy_options[0], 'por', enemy_options[1])
					enemy_options = enemy_options[1:]

				if enemy_options[0]['chance_win'] >= 90:
					fight_multiplier = math.floor(stamina / 40)
				else:
					fight_multiplier = 1

				# res = cryptoblades_contract.functions.fight(char, enemy_options[0]['weapon'], enemy_options[0]['enemy_id'], fight_multiplier).call({'from': my_accounts[2]})
				print(char, enemy_options[0], stamina, fight_multiplier)
	except Exception as e:
		print(e)

	# return HttpResponse('ok')

def wait_random(min=1, max=4):
	seconds = randrange(min, max)
	# print(f'sleeping {seconds} sec')
	sleep(seconds)

WeaponElement = ['Fire', 'Earth', 'Lightning', 'Water']

def getStatPatternFromProperties(properties):
  return (properties >> 5) & 0x7f

def getElementFromProperties(properties):
  return (properties >> 3) & 0x3

def getStarsFromProperties(properties):
  return (properties) & 0x7

def getStat1Trait(statPattern):
  return (statPattern % 5)

def getStat2Trait(statPattern):
  return (math.floor(statPattern / 5) % 5)

def getStat3Trait(statPattern):
  return (math.floor(math.floor(statPattern / 5) / 5) % 5)
	
def trait_power(wElement, sElement, sValue):
	return sValue * (0.002675 if wElement == sElement else 0.002575 if sElement == 'p' else 0.0025)

def weapons_bsc(request):
	total_weapons = market_contract.functions.getNumberOfListingsForToken(web3.toChecksumAddress(weapons_address)).call()
	db = models.Weapon.objects.all()
	initial = 0 # len(db)

	while initial < total_weapons:
		try:
			inserted = 0
			num_results, ids, sellers, prices = market_contract.functions.getListingSlice(web3.toChecksumAddress(weapons_address), initial, num_market_list_per_call).call()
			initial += num_results

			for i in range(num_results):
				weapon_by_id = db.filter(weaponId=ids[i])

				if not weapon_by_id:
					properties, stat1, stat2, stat3, level, blade, crossguard, grip, pommel, burnPoints, bonusPower = weapons_contract.functions.get(ids[i]).call()
					statPattern = getStatPatternFromProperties(properties)

					new = models.Weapon()
					new.price = prices[i] * 1.1 / 1000000000000000000
					new.weaponId = ids[i]
					new.sellerAddress = sellers[i]
					new.weaponStars = getStarsFromProperties(properties)
					new.weaponElement = getElementFromProperties(properties)
					new.stat1Element = getStat1Trait(statPattern)
					new.stat1Value = stat1
					new.stat2Element = getStat2Trait(statPattern)
					new.stat2Value = stat2
					new.stat3Element = getStat3Trait(statPattern)
					new.stat3Value = stat3
					new.power = 1 + trait_power(new.weaponElement, new.stat1Element, new.stat1Value) + trait_power(new.weaponElement, new.stat2Element, new.stat2Value) + trait_power(new.weaponElement, new.stat3Element, new.stat3Value)
					new.powerPerPrice = new.power / new.price
					new.save()
					
					inserted += 1
					db = models.Weapon.objects.all()	
				else:
					w_db = weapon_by_id[0]
					w_db.price = prices[i] * 1.1
					w_db.save()

			print(f'{inserted} new | initial {initial} of {total_weapons}')
		except ValueError as error:
			print("ERROR: ", error)
			wait_random()

	return HttpResponse('ok')

class WeaponView(viewsets.ModelViewSet):  
	serializer_class = WeaponSerializer   
	queryset = models.Weapon.objects.all().order_by('-power')[:10]
	fight(None)

@csrf_exempt
@api_view(['GET', 'POST'])
def update_price(request):
	if request.method == "POST":
		print(request)
		weapon_by_id = models.Weapon.objects.filter(weaponId=request.data.get('weaponId', ''))

		if weapon_by_id:
			w_db = weapon_by_id[0]
			w_db.price = request.data.get('price', '')
			w_db.save()
	
	return HttpResponse('ok')


replacer = {'lightning' : 'l', 'intelligence' : 'l', 'fire' : 'f', 'strength' : 'f', 
						'earth' : 'e','dexterity' : 'e', 'water' : 'w', 'charisma' : 'w', 'power' : 'p'}

def name_trait(name):
	return replacer[name] if name in replacer.keys() else name

def load_weapons(request):
	# for w in models.Weapon.objects.all():
	# 	w.weaponElement = name_trait(w.weaponElement)
	# 	w.stat1Element = name_trait(w.stat1Element)
	# 	w.stat2Element = name_trait(w.stat2Element)
	# 	w.stat3Element = name_trait(w.stat3Element)
	# 	w.power = 1 + trait_power(w.weaponElement, w.stat1Element, w.stat1Value) + trait_power(w.weaponElement, w.stat2Element, w.stat2Value) + trait_power(w.weaponElement, w.stat3Element, w.stat3Value)
	# 	w.save()
	# return HttpResponse('ok')

	page = {
		'curPage': 1,
		'currOffset': 0,
		'pageSize': 60,
		'total': 9999,
    'numPages': 9999
	}
	date_limit_requests = datetime.now()
	quantity_limit_requests = 10

	while page['curPage'] < page['numPages']:
		# print(quantity_limit_requests, '|', date_limit_requests, '|', datetime.now())
		if date_limit_requests.timestamp() < datetime.now().timestamp() or quantity_limit_requests > 0:
			weapons_url = f'https://api.cryptoblades.io/static/market/weapon?element=&minStars=4&maxStars=7&sortBy=price&sortDir=1&pageSize={page["pageSize"]}&pageNum={page["curPage"]}'
			r = requests.get(weapons_url)
			j = json.loads(r.text)

			date_limit_requests = datetime.fromtimestamp(int(r.headers['X-Ratelimit-Reset']))
			quantity_limit_requests = int(r.headers['X-Ratelimit-Remaining'])

			# if page['curPage'] == 2:
			# 	return HttpResponse('ok')
			page = j['page']
			page['curPage'] += 1
			db = models.Weapon.objects.all()
			inserted = 0

			for w in j['results']:
				weapon_by_id = db.filter(weaponId=w['weaponId'])

				if not weapon_by_id:
					new = models.Weapon()
					new.price = w['price'] * 1.1
					new.weaponId = w['weaponId']
					new.sellerAddress = w['sellerAddress']
					new.weaponStars = w['weaponStars']
					new.weaponElement = name_trait(w['weaponElement'])
					new.stat1Element = name_trait(w['stat1Element'])
					new.stat1Value = w['stat1Value']
					new.stat2Element = name_trait(w['stat2Element'])
					new.stat2Value = w['stat2Value']
					new.stat3Element = name_trait(w['stat3Element'])
					new.stat3Value = w['stat3Value']
					new.power = 1 + trait_power(w['weaponElement'], w['stat1Element'], w['stat1Value']) + trait_power(w['weaponElement'], w['stat2Element'], w['stat2Value']) + trait_power(w['weaponElement'], w['stat3Element'], w['stat3Value'])
					new.powerPerPrice = new.power / new.price
					new.save()
					db = models.Weapon.objects.all()	
					inserted += 1
				else:
					w_db = weapon_by_id[0]
					w_db.price = w['price'] * 1.1
					w_db.save()

			print(f'{inserted} new | page {page["curPage"]-1} of {page["numPages"]}')

		wait_random(60/10*0.5, 60/10*1.5)
	
	return HttpResponse('ok')

	
#  "idResults":[
#       "1178075",
#       "1150166",
