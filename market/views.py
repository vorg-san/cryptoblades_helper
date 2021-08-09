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
web3 = Web3(Web3.HTTPProvider('https://bsc-dataseed1.defibit.io/'))

with open(os.path.dirname(__file__) + '\\contracts\\NFTMarket.json') as json_file:
    abi_market = json.load(json_file)['abi']
with open(os.path.dirname(__file__) + '\\contracts\\Weapons.json') as json_file:
    abi_weapons = json.load(json_file)['abi']

market_contract = web3.eth.contract(address=web3.toChecksumAddress(market_address), abi=abi_market)
weapons_contract = web3.eth.contract(address=web3.toChecksumAddress(weapons_address), abi=abi_weapons)
num_market_list_per_call = 3000


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
	initial = 0
	
	db = models.Weapon.objects.all()

	while initial < total_weapons:
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

	return HttpResponse('ok')

class WeaponView(viewsets.ModelViewSet):  
	serializer_class = WeaponSerializer   
	queryset = models.Weapon.objects.all().order_by('-power')[:10]
	# weapons_bsc(None)

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
