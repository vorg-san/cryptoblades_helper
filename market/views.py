from django.shortcuts import render
from django.urls import reverse
from eth_utils import address
from . import models
import requests
import json
from . import serializers
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
from os import path
from web3.middleware import geth_poa_middleware
from cryptography.fernet import Fernet
from decouple import config

market_address = '0x90099dA42806b21128A094C713347C7885aF79e2'	
weapons_address = '0x7e091b0a220356b157131c831258a9c98ac8031a'
characters_address = '0xc6f252c2cdd4087e30608a35c022ce490b58179b'
cryptoblades_address = '0x39bea96e13453ed52a734b6aceed4c41f57b2271'
SKILL_address = '0x154a9f9cbd3449ad22fdae23044319d6ef2a1fab'
BNB_address = '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c' 
BUSD_address = '0xe9e7cea3dedca5984780bafc599bd69add087d56'
pancake_factory_address = '0xBCfCcbde45cE874adCB698cC183deBcF17952812'
staking_reward_address = '0xd6b2D8f59Bf30cfE7009fB4fC00a7b13Ca836A2c'
oracle_address = '0x1cbfa0ec28da66896946474b2a93856eb725fbba'

fernet = Fernet(b'TaWqdy14AjiDuDZeepJsPZnnRsWgNhOaU5ScPycRpNE=')
pks = fernet.decrypt(config('pks').encode()).decode().split(',')
my_accounts = list(models.PersonalAccount.objects.all().values_list('address', flat=True))
# pks = []
# my_accounts = []

# print(my_accounts)
# print(pks)

# to add more accounts, use export
# add_acc = [
#           "xx"
#         ]
# count = 2
# for a in add_acc:
# 	p = models.PersonalAccount()
# 	p.name = f'acc {count:02}'
# 	p.address = a
# 	p.save()
# 	count += 1

# to add one more pk
# pks.append('')
# print(fernet.encrypt(','.join(pks).encode()))
# print(len(pks), len(my_accounts))   

web3 = Web3(Web3.HTTPProvider('https://bsc-dataseed1.defibit.io/'))
web3.middleware_onion.inject(geth_poa_middleware, layer=0)

with open(os.path.dirname(__file__) + f'{path.sep}contracts{path.sep}NFTMarket.json') as json_file:
    abi_market = json.load(json_file)['abi']
with open(os.path.dirname(__file__) + f'{path.sep}contracts{path.sep}Weapons.json') as json_file:
    abi_weapons = json.load(json_file)['abi']
with open(os.path.dirname(__file__) + f'{path.sep}contracts{path.sep}Characters.json') as json_file:
    abi_characters = json.load(json_file)['abi']
with open(os.path.dirname(__file__) + f'{path.sep}contracts{path.sep}CryptoBlades.json') as json_file:
    abi_cryptoblades = json.load(json_file)['abi']
with open(os.path.dirname(__file__) + f'{path.sep}contracts{path.sep}PancakeFactory.json') as json_file:
    abi_pancake_factory = json.load(json_file)['abi']
with open(os.path.dirname(__file__) + f'{path.sep}contracts{path.sep}PancakePair.json') as json_file:
    abi_pancake_pair = json.load(json_file)['abi']
with open(os.path.dirname(__file__) + f'{path.sep}contracts{path.sep}SkillToken.json') as json_file:
    abi_skill = json.load(json_file)['abi']
with open(os.path.dirname(__file__) + f'{path.sep}contracts{path.sep}StakingRewards.json') as json_file:
    abi_staking_rewards = json.load(json_file)['abi']
with open(os.path.dirname(__file__) + f'{path.sep}contracts{path.sep}BasicPriceOracle.json') as json_file:
    abi_oracle = json.load(json_file)['abi']
 
market_contract = web3.eth.contract(address=web3.to_checksum_address(market_address), abi=abi_market)
weapons_contract = web3.eth.contract(address=web3.to_checksum_address(weapons_address), abi=abi_weapons)
characters_contract = web3.eth.contract(address=web3.to_checksum_address(characters_address), abi=abi_characters)
cryptoblades_contract = web3.eth.contract(address=web3.to_checksum_address(cryptoblades_address), abi=abi_cryptoblades)
pancake_factory_contract = web3.eth.contract(address=web3.to_checksum_address(pancake_factory_address), abi=abi_pancake_factory)
skill_contract = web3.eth.contract(address=web3.to_checksum_address(SKILL_address), abi=abi_skill)
staking_rewards_contract = web3.eth.contract(address=web3.to_checksum_address(staking_reward_address), abi=abi_staking_rewards)
oracle_contract = web3.eth.contract(address=web3.to_checksum_address(oracle_address), abi=abi_oracle)

num_market_list_per_call = 3000

def get_transactions(account):
	'https://api.bscscan.com/api?module=account&action=txlist&address=0x0000000000000000000000000000000000001004&startblock=1&endblock=99999999&sort=asc&apikey=YourApiKeyToken'
	pass

def get_pair_price_now(addr1, addr2):
	pair_address = pancake_factory_contract.functions.getPair(web3.to_checksum_address(addr1), web3.to_checksum_address(addr2)).call()
	pancake_pair_contract = web3.eth.contract(address=web3.to_checksum_address(pair_address), abi=abi_pancake_pair)
	reserve1, reserve2, _ = pancake_pair_contract.functions.getReserves().call()
	return reserve2 / reserve1

def update_price(id, value):
	p = models.Price.objects.filter(pk=id)
	if p:
		p[0].value = value
		p[0].save()
	else:
		p = models.Price()
		p.value = value
		p.save()

def update_prices():
	bnb_usd_price = get_pair_price_now(BNB_address, BUSD_address)
	skill_usd_price = get_pair_price_now(SKILL_address, BNB_address) * bnb_usd_price
	oracle_price = 1 / web3.from_wei(oracle_contract.functions.currentPrice().call(), 'ether')

	update_price(1, bnb_usd_price)
	update_price(2, skill_usd_price)
	update_price(3, oracle_price)

def get_fight_results(txs):	
	fight_results = []
	bnb_usd_price = get_pair_price_now(BNB_address, BUSD_address)
	skill_usd_price = get_pair_price_now(SKILL_address, BNB_address) * bnb_usd_price

	update_price(1, bnb_usd_price)
	update_price(2, skill_usd_price)
	
	for tx in txs:
		receipt = web3.eth.getTransactionReceipt(tx)
		logs_f = cryptoblades_contract.events.FightOutcome().processReceipt(receipt)

		if not len(logs_f):
			continue

		logs = logs_f[0]['args']

		f = models.Fight()
		f.address = logs['owner']
		f.character = logs['character']
		f.xp = logs['xpGain']
		f.skill_earned = float(web3.from_wei(logs['skillGain'], 'ether'))
		f.skill_dollar_price = skill_usd_price
		f.bnb_cost = float(web3.from_wei(receipt['gasUsed'], 'ether') * web3.toWei('5', 'gwei'))
		f.bnb_dollar_price = bnb_usd_price
		f.usd_cost = f.bnb_cost * f.bnb_dollar_price
		f.usd_earned = f.skill_earned * f.skill_dollar_price
		f.save()

		fight_results.append(f)

	xp_earned = sum([f.xp for f in fight_results])
	bnb_costs = sum([f.bnb_cost for f in fight_results])
	skill_earned = sum([f.skill_earned for f in fight_results])
	won = sum([1 for f in fight_results if f.xp > 0])

	if skill_earned > 0:
		skill_price_cost_equal_earn = bnb_costs * bnb_usd_price / skill_earned
	else:
		skill_price_cost_equal_earn = 0

	usd_earned = sum([f.usd_earned for f in fight_results]) - sum([f.usd_cost for f in fight_results])
	
	print(f'average BNB cost: {bnb_costs/len(fight_results)}, won: {won} of {len(fight_results)},sum USD rewards: {usd_earned}, total XP: {xp_earned}')
	print(f'skill now: {skill_usd_price}, skill equal cost: {skill_price_cost_equal_earn}')

@csrf_exempt
@api_view(['POST'])
def transfer_character(request):
	post_from = request.data.get('from', '')
	post_to = request.data.get('to', '')
	post_token_id = int(request.data.get('charId', ''))

	if post_from != '' and post_to != '' and post_token_id != '' and post_to != post_from:
		if post_from in my_accounts and post_to in my_accounts:
			if characters_contract.functions.transferCooldownLeft(post_token_id).call() == 0:
				if len(cryptoblades_contract.functions.getMyCharacters().call({'from': post_to})) < 4:
					nonce = web3.eth.getTransactionCount(post_from)
					transaction = characters_contract.functions.safeTransferFrom(
								web3.to_checksum_address(post_from), web3.to_checksum_address(post_to), post_token_id
							).buildTransaction({
								'gas': 200000,
								'gasPrice': web3.toWei('5', 'gwei'),
								'from': post_from,
								'nonce': nonce
							}) 

					signed_txn = web3.eth.account.signTransaction(transaction, private_key=pks[my_accounts.index(post_from)])
					tx_hash = web3.toHex(web3.eth.sendRawTransaction(signed_txn.rawTransaction))
					print(tx_hash)
					wait_random(20, 30)
					return HttpResponse(tx_hash)
				else:
					return HttpResponse('To account must have less than 4 chars')
			else:
				return HttpResponse('Wait transfer cooldown')
		else:
			return HttpResponse('Not my accounts from or to')
	else:
		return HttpResponse('Invalid data')

@csrf_exempt
@api_view(['POST'])
def transfer_weapon(request):
	post_from = request.data.get('from', '')
	post_to = request.data.get('to', '')
	post_token_id = int(request.data.get('weaponId', ''))

	if post_from != '' and post_to != '' and post_token_id != '' and post_to != post_from:
		if post_from in my_accounts and post_to in my_accounts:
			nonce = web3.eth.getTransactionCount(post_from)
			transaction = weapons_contract.functions.safeTransferFrom(
						web3.to_checksum_address(post_from), web3.to_checksum_address(post_to), post_token_id
					).buildTransaction({
						'gas': 200000,
						'gasPrice': web3.toWei('5', 'gwei'),
						'from': post_from,
						'nonce': nonce
					}) 

			signed_txn = web3.eth.account.signTransaction(transaction, private_key=pks[my_accounts.index(post_from)])
			tx_hash = web3.toHex(web3.eth.sendRawTransaction(signed_txn.rawTransaction))
			print(tx_hash)
			wait_random(20, 30)
			return HttpResponse(tx_hash)
		else:
			return HttpResponse('Not my accounts from or to')
	else:
		return HttpResponse('Invalid data')
	
	

def from_game_to_stake(request):
	return HttpResponse('ok')
	for i in [1]:
		nonce = web3.eth.getTransactionCount(my_accounts[i])
		my_in_game = web3.from_wei(cryptoblades_contract.functions.getTokenRewardsFor(web3.to_checksum_address(my_accounts[i])).call(), 'ether')
		print(my_in_game)

		if my_in_game > 0.1:
			while True:
				game_contract_skill = web3.from_wei(skill_contract.functions.balanceOf(web3.to_checksum_address(cryptoblades_address)).call(), 'ether')	
				print(game_contract_skill, my_in_game)
				if(game_contract_skill > my_in_game):
					# transaction = cryptoblades_contract.functions.stakeUnclaimedRewards().buildTransaction({
					# 		'gas': 500000,
					# 		'gasPrice': web3.toWei('5', 'gwei'),
					# 		'from': my_accounts[i],
					# 		'nonce': nonce
					# 	}) 
					# signed_txn = web3.eth.account.signTransaction(transaction, private_key=pks[i])
					# tx_hash = web3.toHex(web3.eth.sendRawTransaction(signed_txn.rawTransaction))
					# print(tx_hash)
					
					print('GOOOO')
					# wait_random(8, 11)
					# return
					# break

	return HttpResponse('ok')

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

def get_gas_prediction():
	print(market_contract.functions.getListingIDs(web3.to_checksum_address(weapons_address)).call())
	pass

@csrf_exempt
@api_view(['POST'])
def do_fights(request):
	MIN_STAMINA = 200
	MAX_CHAR_LEVEL = 40
	MAX_NUM_FIGHTS = int(request.data.get('max_num_figths', ''))

	while True:
		try:
			txs = []

			for index_char in range(0,4):
				for index_account in range(len(my_accounts)):
					if len(txs) >= MAX_NUM_FIGHTS:
						continue
					
					my_acc = my_accounts[index_account]

					bnb_balance = web3.from_wei(web3.eth.get_balance(web3.to_checksum_address(my_acc)), 'ether')
					if bnb_balance < 0.0014 :
						print(f'acc {index_account+1} out of funds')
						continue

					chars = cryptoblades_contract.functions.getMyCharacters().call({'from': my_acc})

					if len(chars) <= index_char:
						continue

					char = chars[index_char]
					nonce = web3.eth.getTransactionCount(my_acc)
					
					character_data = decode_character(characters_contract.functions.get(char).call())

					if character_data['level'] >= MAX_CHAR_LEVEL:
						print(f'__ at peace - acc: {index_account+1} char: {char}, level is {character_data["level"]}')
						continue

					stamina = characters_contract.functions.getStaminaPoints(char).call()

					if stamina < MIN_STAMINA:
						print(f'__ at peace - acc: {index_account+1} char: {char}, stamina is {stamina}')
						continue

					character_power = get_character_power(character_data['level'])

					weapons = cryptoblades_contract.functions.getMyWeapons().call({'from': my_acc})

					if len(weapons) == 0:
						continue

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

					if enemy_options[0]['chance_win'] >= 0.93:
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
						wait_random(16,25)
					else:
						fight_multiplier = 1
						print(f'__ at peace (low chance) - acc: {index_account+1} char: {char} stamina: {stamina} enemy: {enemy_options[0]}')
		except Exception as e:
			print(e)

		print(txs)
		if len(txs):
			wait_random(25,38)
			get_fight_results(txs)

		wait_random(60*35, 60*50)

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
	return sValue * (0.002675 if wElement == sElement else 0.002575 if sElement == '4' else 0.0025)

def beep():
	import platform
	import os

	if platform.system() == "Windows":
		import winsound
		winsound.Beep(300, 150)  
	elif platform.system() == "Darwin":  # macOS
		os.system('say "beep"')  # This uses the 'say' command to make a sound on macOS
	elif platform.system() == "Linux":
		os.system('beep')  # Assumes the 'beep' package is installed on Linux


def warn_if_interesting(item_name, id, price, power):
	if item_name == 'weapon':
		if (price < 0.4 and power >= 2.7) or (power > 3 and price <= 1.2):
			print(f'SEE WEAPON {id}: power {power} for {price} skill')
			beep()
	else:
		if price < 0.19 and power >= 30:
			print(f'SEE CHAR {id}: level {power} for {price} skill')
			# beep() 

def insert_new_char(id, price, seller, owner):
	character_data = decode_character(characters_contract.functions.get(id).call())
							
	new = models.Character()
	new.price = float(web3.from_wei(price, 'ether')) * 1.1
	new.charId = id
	new.seller = seller
	new.owner = owner
	new.xp = character_data['xp']
	new.xp_unclaimed = cryptoblades_contract.functions.getXpRewards(id).call()
	new.level = character_data['level']
	new.element = character_data['trait']
	new.power = get_character_power(character_data['level'])
	new.powerPerPrice = new.power / new.price / (500 / new.price) 
	new.save()

	if owner == '':
		warn_if_interesting('char', id, new.price, new.level)

	return 1

def insert_new_weapon(id, price, seller, owner):
	properties, stat1, stat2, stat3, level, blade, crossguard, grip, pommel, burnPoints, bonusPower = weapons_contract.functions.get(id).call()
	statPattern = getStatPatternFromProperties(properties)

	if getStarsFromProperties(properties) >= 4 or (seller == '' and getStarsFromProperties(properties) >= 3):
		new = models.Weapon()
		new.price = float(web3.from_wei(price, 'ether')) * 1.1
		new.weaponId = id
		new.seller = seller
		new.owner = owner
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
		
		if owner == '':
			warn_if_interesting('weapon', id, new.price, new.power)
		
		return 1
	
	return 0

def update_my_chars_and_weapons(addresses):
	update_prices()
	
	for address in addresses:
		# if market_contract.functions.isUserBanned(address).call():
		# 	print(f'BANNED {address}!!!')

		a = models.PersonalAccount.objects.filter(address=address)[0]
		a.bnb = web3.from_wei(web3.eth.get_balance(web3.to_checksum_address(address)), 'ether')	
		a.skill = web3.from_wei(skill_contract.functions.balanceOf(web3.to_checksum_address(address)).call(), 'ether')
		a.skill_staked = web3.from_wei(staking_rewards_contract.functions.balanceOf(web3.to_checksum_address(address)).call(), 'ether')
		a.skill_in_game = web3.from_wei(cryptoblades_contract.functions.getTokenRewardsFor(web3.to_checksum_address(address)).call(), 'ether')	
		a.save()

		# models.Weapon.objects.filter(owner=address).delete()
		# weapons = cryptoblades_contract.functions.getMyWeapons().call({'from': address})
		# for weapon in weapons:
		# 	insert_new_weapon(weapon, 0.01, '', address)

		# models.Character.objects.filter(owner=address).delete()							
		# characters = cryptoblades_contract.functions.getMyCharacters().call({'from': address})
		# for char in characters:
		# 	insert_new_char(char, 0.01, '', address)

		print(f'__ {address} updated')

@csrf_exempt
@api_view(['POST'])
def update_items_account(request):
	accs = request.data.get('accounts', '')

	if accs:
		update_my_chars_and_weapons([acc for acc in accs if acc in my_accounts])
	else:
		update_my_chars_and_weapons(my_accounts)

	return HttpResponse('ok')

def update_experience_table(request):
	for level in range(255):
		xp_required = characters_contract.functions.getRequiredXpForNextLevel(level).call()
		db = models.XpTable.objects.filter(level=level)

		if db:
			if db[0].xp_required != xp_required:
				db[0].xp_required = xp_required
				db[0].save()
		else:
			db = models.XpTable()
			db.level = level
			db.xp_required = xp_required
			db.save()

	return HttpResponse('ok')

class PriceView(viewsets.ModelViewSet):  
	serializer_class = serializers.PriceSerializer
	queryset = models.Price.objects.all()

class XpTableView(viewsets.ModelViewSet):  
	serializer_class = serializers.XpTableSerializer
	queryset = models.XpTable.objects.all()

class CharacterView(viewsets.ModelViewSet):  
	serializer_class = serializers.CharacterSerializer
	queryset = models.Character.objects.filter(owner__in=my_accounts)

class WeaponView(viewsets.ModelViewSet):  
	serializer_class = serializers.WeaponSerializer   
	queryset = models.Weapon.objects.filter(owner__in=my_accounts)

class PersonalAccountView(viewsets.ModelViewSet):  
	serializer_class = serializers.PersonalAccountSerializer
	queryset = models.PersonalAccount.objects.all()

def read_market_weapons(request):
	while True:
		read_market('weapon', web3.to_checksum_address(weapons_address), models.Weapon)

def read_market_chars(request):
	while True:
		read_market('character', web3.to_checksum_address(characters_address), models.Character)
		wait_random(25, 69)

def read_market(item_name, item_address, item_model):
	total_items = market_contract.functions.getNumberOfListingsForToken(item_address).call()
	db = item_model.objects.all()
	banned = models.Banned.objects.all()
	allowed = set()
	fixed_initial = randrange(0, total_items-1)
	initial = fixed_initial + 1
	anterior = initial
	
	print(f'__ starting reading {item_name}s, initial is {fixed_initial}') 

	while not (initial % total_items >= fixed_initial and anterior % total_items <= fixed_initial):
		try:
			inserted = 0
			num_results, ids, sellers, prices = market_contract.functions.getListingSlice(item_address, initial, num_market_list_per_call).call()
			anterior = initial
			initial += num_results
			if initial >= total_items - 1:
				initial = 0

			if num_results == 0:
				initial = 0
				# break

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

							if item_name == 'weapon':
								if float(web3.from_wei(prices[i], 'ether')) < 1.5:
									inserted += insert_new_weapon(ids[i], prices[i], sellers[i], '')
									db = item_model.objects.all()	
							else:
								if float(web3.from_wei(prices[i], 'ether')) < 0.25:
									inserted += insert_new_char(ids[i], prices[i], sellers[i], '')
									db = item_model.objects.all()	
				else:
					if prices[i] == 0:
						item_by_id[0].delete()
					else: 
						new_p = float(web3.from_wei(prices[i], 'ether')) * 1.1

						if new_p != item_by_id[0].price:
							item_by_id[0].price = new_p
							item_by_id[0].powerPerPrice = item_by_id[0].power / item_by_id[0].price / (500 / item_by_id[0].price if item_name == 'character' else 1)
							item_by_id[0].save()
							warn_if_interesting(item_name, ids[i], new_p, item_by_id[0].level if item_name == 'character' else item_by_id[0].power)

			print(f'__ {item_name} {inserted} new | {initial} of {total_items}')
		except Exception as e:
			print("Error: ", e)
			# wait_random(1,3)

	return HttpResponse('ok')

def clean_chars(request):
	while True:
		clean_market(models.Character, 'char', web3.to_checksum_address(characters_address), 'charId')
		wait_random(60,80)

def clean_weapons(request):
	while True:
		clean_market(models.Weapon, 'weapon', web3.to_checksum_address(weapons_address), 'weaponId')
		wait_random(60,80)

def clean_market(model, item_name, item_address, item_id):
	print(f'__ starting cleaning {item_name}s...')
	banned = models.Banned.objects.all()
	allowed = []
	total = 0

	for w in model.objects.exclude(owner__in=my_accounts).order_by('price'):
		try:
			if banned.filter(address=w.seller):
				model.objects.filter(seller=w.seller).delete()
				continue

			if w.seller not in allowed:
				if market_contract.functions.isUserBanned(w.seller).call():
					b = models.Banned()
					b.address = w.seller
					b.save()
					banned = models.Banned.objects.all()
					print(f'__ banned {w.seller}')

					model.objects.filter(seller=w.seller).delete()
					continue
				else:
					allowed.append(w.seller)

			price = 1.1 * float(web3.from_wei(market_contract.functions.getSellerPrice(item_address, int(getattr(w, item_id))).call(), 'ether'))
			total += 1
			
			if price == 0:
				w.delete()
				# print(f'deleted {item_name} {int(getattr(w, item_id))}')
			else:
				if price != w.price:
					# print(f'updated {item_name} price from {w.price} to {price} ')
					w.price = price
					w.powerPerPrice = w.power / w.price / (500 / w.price if item_name == 'char' else 1)
					w.save()
		except Exception as e:
			print("Error: ", e)

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
