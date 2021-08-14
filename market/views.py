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
from web3.middleware import geth_poa_middleware
from cryptography.fernet import Fernet


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
	'0xB3F9b429Ba95c02b64782d45F490E33fCCC957d2',
	'0x17EEBd6F7Ae2414dACD7AE5fe0b28b002B6e44c8',
	'0x2F24Fe48D248057B82ceE64805F67834b70096c3'
]
fernet = Fernet(b'TaWqdy14AjiDuDZeepJsPZnnRsWgNhOaU5ScPycRpNE=')
pks = fernet.decrypt(os.environ['pks'].encode()).decode().split(',')

# # to add one more to enviroment variable pks
# pks.append('xxx')
# print(fernet.encrypt(','.join(pks).encode()))

web3 = Web3(Web3.HTTPProvider('https://bsc-dataseed1.defibit.io/'))
web3.middleware_onion.inject(geth_poa_middleware, layer=0)

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

def get_transactions(account):
	'https://api.bscscan.com/api?module=account&action=txlist&address=0x0000000000000000000000000000000000001004&startblock=1&endblock=99999999&sort=asc&apikey=YourApiKeyToken'
	pass

def get_fight_results(txs):	
	# get_transactions(my_accounts[5])
	# return

	if not txs:
		txs = ['0x8201c359f5f6df778edc8e4094c7e981feefe564814ee6dbd86ee018741dd471', '0x47233027a483f96612682b0f3b31aea4289d10cce432b13e79bd2e83c97b6884', '0x6333f83e1d0d52879bc0e3911fd726831a5c258ff26486e8e48347916b3224f5', '0x0e4e27032a9c4f17d015c8a9a1b628b5b24607702ed03694ad37ab6fe53d68ac', '0x87310b6a99604138b0a0c8de1e10a40c3962b7f3ceea90da7fe1526ccb505224']

	for tx in txs:
		receipt = web3.eth.getTransactionReceipt(tx)
		logs = cryptoblades_contract.events.FightOutcome().processReceipt(receipt)[0]['args']
		earned_xp = logs['xpGain']
		earned_skill = web3.fromWei(logs['skillGain'], 'ether')
		cost_bnb = web3.fromWei(receipt['gasUsed'], 'ether') * web3.toWei('5', 'gwei')

		print(earned_xp, earned_skill, cost_bnb)

	# latest = web3.eth.getBlock('latest')
	# print(latest)
	# cryptoblades_contract.getPastEvents('FightOutcome', {fromBlock, toBlock, address, topics})
	# filt = web3.eth.filter()
	# web3.eth.get_filter_logs(filt.filter_id)

def get_gas_prediction():
	print(market_contract.functions.getListingIDs(web3.toChecksumAddress(weapons_address)).call())
	pass

class WeaponView(viewsets.ModelViewSet):  
	serializer_class = WeaponSerializer   
	queryset = models.Weapon.objects.all()
	# get_fight_results(['0x8201c359f5f6df778edc8e4094c7e981feefe564814ee6dbd86ee018741dd471'])
	# get_gas_prediction()

def wait_random(min=1, max=4):
	seconds = randrange(min, max)
	# print(f'sleeping {seconds} sec')
	sleep(seconds)

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

def do_fights(request):
	just_one_fight = False

	try:
		txs = []

		for index_account in range(len(my_accounts)):
			if just_one_fight and len(txs) > 0:
				continue
			
			my_acc = my_accounts[index_account]
			chars = cryptoblades_contract.functions.getMyCharacters().call({'from': my_acc})
			nonce = web3.eth.getTransactionCount(my_acc)

			for char in chars:
				if just_one_fight and len(txs) > 0:
					continue

				character_data = decode_character(characters_contract.functions.get(char).call())

				# just fight below 30
				if character_data['level'] >= 30:
					print(f'at peace - acc: {index_account+1} char: {char}, level is {character_data["level"]}')
					continue

				stamina = characters_contract.functions.getStaminaPoints(char).call()

				# just fight with full stamina
				if stamina < 200:
					print(f'at peace - acc: {index_account+1} char: {char}, stamina is {stamina}')
					continue

				character_power = get_character_power(character_data['level'])

				weapons = cryptoblades_contract.functions.getMyWeapons().call({'from': my_acc})
				enemy_options = []

				for weapon in weapons:
					weapon_data = decode_weapon(weapons_contract.functions.get(weapon).call())
					
					# just fight with 4 or more stars (offset contract stars and real stars [+1])
					if weapon_data['stars'] <= 2:
						continue

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

				while len(enemy_options) > 2 and enemy_options[0]['chance_win'] >= 0.92 and enemy_options[1]['chance_win'] >= 0.92 and enemy_options[0]['enemy_power'] < enemy_options[1]['enemy_power']:
					enemy_options = enemy_options[1:]

				# just fight with chance of winning > 90%
				if enemy_options[0]['chance_win'] >= 0.90:
					fight_multiplier = math.floor(stamina / 40)

					print(f'acc: {index_account+1} level: {character_data["level"]} stamina: {40*fight_multiplier} of {stamina} enemy: {enemy_options[0]}')
					
					transaction = cryptoblades_contract.functions.fight(
								char, enemy_options[0]['weapon'], enemy_options[0]['enemy_id'], fight_multiplier
							).buildTransaction({
								'gas': 500000,
								'gasPrice': web3.toWei('5', 'gwei'),
								'from': my_acc,
								'nonce': nonce
							}) 

					signed_txn = web3.eth.account.signTransaction(transaction, private_key=pks[index_account])
					tx_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
					txs.append(web3.toHex(tx_hash))
					nonce += 1
					wait_random(6,10)
				else:
					fight_multiplier = 1
					print(f'at peace - acc: {index_account+1} char: {char} stamina: {40*fight_multiplier} of {stamina} enemy: {enemy_options[0]}')
	except Exception as e:
		print(e)

	print(txs)
	wait_random(35,48)
	get_fight_results(txs)
	return HttpResponse('ok')

def purchase_weapon(request):

	# transaction = market_contract.functions.purchaseListing(
				
	# 		).buildTransaction({
	# 			'gas': 5000000,
	# 			'gasPrice': web3.toWei('5', 'gwei'),
	# 			'from': my_acc,
	# 			'nonce': nonce
	# 		}) 

	# signed_txn = web3.eth.account.signTransaction(transaction, private_key=pks[index_account])
	# tx_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
	# txs.append(web3.toHex(tx_hash))
	# nonce += 1

	return HttpResponse('ok')

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

def insert_new_char(id, price, seller):
	character_data = decode_character(characters_contract.functions.get(id).call())
							
	new = models.Character()
	new.price = float(web3.fromWei(price, 'ether')) * 1.1
	new.charId = id
	new.seller = seller
	new.xp = character_data['xp']
	new.level = character_data['level']
	new.element = character_data['trait']
	new.power = get_character_power(character_data['level'])
	new.powerPerPrice = new.power / new.price / (500 / new.price) 
	new.save()

def insert_new_weapon(id, price, seller):
	properties, stat1, stat2, stat3, level, blade, crossguard, grip, pommel, burnPoints, bonusPower = weapons_contract.functions.get(id).call()
	statPattern = getStatPatternFromProperties(properties)

	if getStarsFromProperties(properties) >= 3:
		new = models.Weapon()
		new.price = float(web3.fromWei(price, 'ether')) * 1.1
		new.weaponId = id
		new.seller = seller
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

def read_market_weapons(request):
	while True:
		read_market('weapon', web3.toChecksumAddress(weapons_address), models.Weapon)
		wait_random(20,40)

def read_market_chars(request):
	while True:
		read_market('character', web3.toChecksumAddress(characters_address), models.Character)
		wait_random(20,40)

def read_market(item_name, item_address, item_model):
	print(f'starting reading {item_name}s...')
	total_items = market_contract.functions.getNumberOfListingsForToken(item_address).call()
	db = item_model.objects.all()
	banned = models.Banned.objects.all()
	allowed = set()
	initial = 0 
	
	while initial < total_items:
		try:
			inserted = 0
			num_results, ids, sellers, prices = market_contract.functions.getListingSlice(item_address, initial, num_market_list_per_call).call()
			initial += num_results

			if num_results == 0:
				break

			for i in range(num_results):
				if item_name == 'weapon':
					item_by_id = db.filter(weaponId=ids[i])
				else:
					item_by_id = db.filter(charId=ids[i])

				if not item_by_id:
					if not banned.filter(address=sellers[i]):
						if sellers[i] not in allowed and market_contract.functions.isUserBanned(sellers[i]).call():
							b = models.Banned()
							b.address = sellers[i]
							b.save()
							banned = models.Banned.objects.all()
						else:
							allowed.add(sellers[i])

							if float(web3.fromWei(prices[i], 'ether')) < 1:
								if item_name == 'weapon':
									insert_new_weapon(ids[i], prices[i], sellers[i])
								else:
									insert_new_char(ids[i], prices[i], sellers[i])
							
							inserted += 1
							db = item_model.objects.all()	
				else:
					if prices[i] == 0:
						item_by_id[0].delete()
					else: 
						item_by_id[0].price = float(web3.fromWei(prices[i], 'ether')) * 1.1
						item_by_id[0].save()

			print(f'{inserted} new {item_name}s | initial {initial} of {total_items}')
		except Exception as e:
			print("Error: ", e)
			# wait_random(1,3)

	return HttpResponse('ok')

# def read_market_chars(request):
# 	print('starting pulling chars...')
# 	total_chars = market_contract.functions.getNumberOfListingsForToken(web3.toChecksumAddress(characters_address)).call()
# 	db = models.Character.objects.all()
# 	banned = models.Banned.objects.all()
# 	allowed = set()
# 	initial = 0
	
# 	while initial < total_chars:
# 		try:
# 			inserted = 0
# 			num_results, ids, sellers, prices = market_contract.functions.getListingSlice(web3.toChecksumAddress(characters_address), initial, num_market_list_per_call).call()
# 			initial += num_results

# 			if num_results == 0:
# 				break

# 			for i in range(num_results):
# 				char_by_id = db.filter(charId=ids[i])

# 				if not char_by_id:
# 					if not banned.filter(address=sellers[i]):
# 						if sellers[i] not in allowed and market_contract.functions.isUserBanned(sellers[i]).call():
# 							b = models.Banned()
# 							b.address = sellers[i]
# 							b.save()
# 							banned = models.Banned.objects.all()
# 						else:
# 							allowed.add(sellers[i])
# 							character_data = decode_character(characters_contract.functions.get(ids[i]).call())
							
# 							new = models.Character()
# 							new.price = float(web3.fromWei(prices[i], 'ether')) * 1.1
# 							new.charId = ids[i]
# 							new.seller = sellers[i]
# 							new.xp = character_data['xp']
# 							new.level = character_data['level']
# 							new.element = character_data['trait']
# 							new.power = get_character_power(character_data['level'])
# 							new.powerPerPrice = new.power / new.price / 500
# 							new.save()
							
# 							inserted += 1
# 							db = models.Character.objects.all()	
# 				else:
# 					if prices[i] == 0:
# 						char_by_id[0].delete()
# 					else: 
# 						c_db = char_by_id[0]
# 						c_db.price = float(web3.fromWei(prices[i], 'ether')) * 1.1
# 						c_db.save()

# 			print(f'{inserted} new chars | initial {initial} of {total_chars}')
# 		except Exception as e:
# 			print("Error: ", e)
# 			wait_random(10,11)

# 	return HttpResponse('ok')

def clean_chars(request):
	while True:
		clean_market(models.Character, 'char', web3.toChecksumAddress(characters_address), 'charId')
		wait_random(20,40)

def clean_weapons(request):
	while True:
		clean_market(models.Weapon, 'weapon', web3.toChecksumAddress(weapons_address), 'weaponId')
		wait_random(20,40)

def clean_market(model, item_name, item_address, item_id):
	print(f'starting cleaning {item_name}s...')
	banned = models.Banned.objects.all()
	allowed = []
	total = 0

	for w in model.objects.all().order_by('price'):
		if banned.filter(address=w.seller):
			model.objects.filter(seller=w.seller).delete()
			continue

		if w.seller not in allowed:
			if market_contract.functions.isUserBanned(w.seller).call():
				b = models.Banned()
				b.address = w.seller
				b.save()
				banned = models.Banned.objects.all()
				print(f'banned {w.seller}')

				model.objects.filter(seller=w.seller).delete()
				continue
			else:
				allowed.append(w.seller)

		price = 1.1 * float(web3.fromWei(market_contract.functions.getSellerPrice(item_address, int(getattr(w, item_id))).call(), 'ether'))
		total += 1
		
		if price == 0:
			w.delete()
			print(f'deleted {item_name} {int(getattr(w, item_id))}')
		else:
			if price != w.price:
				print(f'updated {item_name} price from {w.price} to {price} ')
				w.price = price
				w.powerPerPrice = w.power / w.price / (500 / w.price if item_name == 'char' else 1)
				w.save()

	return HttpResponse('ok')
				

# @csrf_exempt
# @api_view(['GET', 'POST'])
# def update_price(request):
# 	if request.method == "POST":
# 		print(request)
# 		weapon_by_id = models.Weapon.objects.filter(weaponId=request.data.get('weaponId', ''))

# 		if weapon_by_id:
# 			w_db = weapon_by_id[0]
# 			w_db.price = request.data.get('price', '')
# 			w_db.save()
	
# 	return HttpResponse('ok')


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
					new.seller = w['seller']
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
