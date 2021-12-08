import math
from . import models
from django.http import HttpResponse
from django.core import serializers
from functools import reduce
import matplotlib.pyplot as plt
from scipy import stats
import json
import mysql.connector
import traceback
from datetime import datetime, timedelta
import time
from collections import defaultdict
from prettytable import PrettyTable

BD_PASS = 'Shaman34#'
mydb = None

def abrir_conexao():
    global mydb
    mydb = mysql.connector.connect(user='root', password=BD_PASS,host='127.0.0.1', database='cryptoblades')

def fechar_conexao():
    mydb.close()

def insertxxx(idManga, titulo, url):
    c = mydb.cursor(dictionary=True)
    c.execute("insert into capitulo(manga_id, titulo, url, data) values(%s, %s, %s, CURRENT_TIMESTAMP()) ", 
                (idManga, titulo, url))
    mydb.commit()

def group_by(r, column):
	groups = defaultdict(list)
	for obj in r:
			groups[obj[column]].append(obj)
	return groups.values()

def get_last_pulls_pancakeswap(qty_last_pulls):
	c = mydb.cursor(dictionary=True)
	c.execute(
		"select c.id, c.link, d.price, d.volume, d.market_cap, p.created " + 
		"from cmc_crypto c  " + 
		"    join cmc_data d on d.crypto_id = c.id " + 
		"    join ( " + 
		"        select id, created " + 
		"        from cmc_pull  " + 
		"        order by id desc limit 0, %s " + 
		"        ) p on p.id = d.pull_id  " + 
		"    join cmc_delta del on del.data2_id = d.id " + 
		"    join ( " + 
		"        select c.id  " + 
		"        from cmc_exchange ce  " + 
		"            join cmc_cryptoexchange cc on ce.id = cc.exchange_id  " + 
		"            join cmc_crypto c on c.id = cc.crypto_id  " + 
		"        where ce.id = 7 " + 
		"        group by c.id " + 
		"    ) ps on ps.id = c.id " + 
		# "where c.id in (8) " + 
		# "where c.source_code is not null " + 
		"order by c.id, p.created  ",
		(qty_last_pulls,)
	)
	r = group_by(c.fetchall(), 'id')
	return r

def get_cryptos():
    c = mydb.cursor(dictionary=True)
    c.execute(
			"select id, name, link " + 
			"from cmc_crypto ", 
			()
		)
    r = c.fetchall()
    return r

def get_dados(id_crypto):
    c = mydb.cursor(dictionary=True)
    c.execute(
			"select p.created, d.price, del.volume  " + 
			"from cmc_data d " + 
			"  join cmc_pull p on p.id = d.pull_id  " + 
			"  join cmc_delta del on del.data2_id = d.id " + 
			"where d.crypto_id = %s ", 
			(id_crypto,)
		)
    r = c.fetchall()
    return r

def is_match(d, target, i):
	res = True
	for j in range(len(target)):
		if d[i+j] < target[j]:
			res = False
	return res

def profile_match(dados, target, column):
	d = [x[column] for x in dados]
	res = [False] * len(dados)

	for i in range(len(d) - len(target)):
		if is_match(d, target, i):
			for j in range(len(target)):
				res[i+j] = True

	return res

def result_if_operate_match(dados, matches, match_pattern):
	if True not in matches:
		return (0, 100)

	pattern_size = len(match_pattern)
	initial = 100
	bought = 0
	previous_match = 0
	total_buys = 0

	for i in range(len(matches)):
		previous_match = previous_match + 1 if matches[i] else 0
		# print(dados[i], matches[i])
		if previous_match >= pattern_size and initial > 0:
			bought = initial / dados[i]['price']
			initial = 0
			total_buys += 1
			# print(f'bought {bought} at price {dados[i]["price"]}')
		if initial == 0 and  dados[i]['volume'] < - 10:
			initial = bought * dados[i]['price']
			bought = 0
			# print(f'sold {initial} at price {dados[i]["price"]}')

	if bought > 0:
		initial = bought * dados[i]['price']
		bought = 0
		# print(f'sold {initial} at price {dados[i]["price"]}')

	return (total_buys, int(initial))

def adjust_data_points(dados):
	return dados

def run():
	target_vol_min = [8,8,8]
	target_column = 'volume'

	for c in get_cryptos():
		dados = adjust_data_points(get_dados(c['id']))
		matches = profile_match(dados, target_vol_min, target_column)
		print(c['id'], c['name'], c['link'], result_if_operate_match(dados, matches, target_vol_min))

	# for i, d in enumerate(dados):
	# 	print(d, matches[i])

def growing(p):
	r = 0
	for i in range(1, len(p)):
		for j in range(i-1, -1, -1):
			if p[i] > p[j]:
				r += 1
	return r


def alert_growing_ps():
	good_ones = []
	for c in get_last_pulls_pancakeswap(5):
		prices = [p['price'] for p in c]
		p = growing(prices)
		v = growing([p['volume'] for p in c])
		vol = (c[0]['volume']+c[-1]['volume'])/2
		mc = c[-1]['market_cap']
		
		if p > 6 and vol > 50000 and mc > 40000 and mc < 50 * 1000000: #and v > 7
			good_ones.append({
				'c': c[0]['link'], 
				'pump': int(100*(c[-1]['price']-min(prices))/min(prices)), 
				'p': p, 
				'v': v, 
				'vol': round(vol/1000000,2),
				'mc': round(mc/1000000,2)
			})
	
	# good_ones.sort(key=lambda x: x['v']+x['p']-x['pump']/10, reverse=True)
	good_ones.sort(key=lambda x: x['mc'], reverse=True)
	
	t = PrettyTable(['Link', 'pump', 'up', 'mc', 'vol'])	
	for g in good_ones:
		t.add_row([g["c"], f'{g["pump"]}%', f'{g["p"]} {g["v"]}', f'{g["mc"]}M', f'{g["vol"]}M'])
	print(t)


def fill_data_each_hour(data, hours_period):
	for c in data:
		start = c['data'][0]['created']
		end = c['data'][-1]['created']
		data_points = []
		while start < end + timedelta(hours = 1):
			data_points.append({'created': start, 'price': 0, 'volume': 0, 'market_cap': 0})
			start += timedelta(hours = 1)

		for i in range(len(c['data'])):
			for j in range(len(data_points)):
				if data_points[j]['created'] - timedelta(hours = 0.5) <= c['data'][i]['created'] <= data_points[j]['created'] + timedelta(hours = 0.5):
					k = j
					while k >= 0 and data_points[k]['price'] == 0:
						k -= 1
					last_k_filled = k

					k = j
					while k > last_k_filled:
						if k == j:
							data_points[k]['price'] = c['data'][i]['price']
							data_points[k]['volume'] = c['data'][i]['volume']
							data_points[k]['market_cap'] = c['data'][i]['market_cap']
						else:
							data_points[k]['price'] = c['data'][i]['price'] + (j-k) * (data_points[last_k_filled]['price'] - c['data'][i]['price']) / (j-last_k_filled)
							data_points[k]['volume'] = c['data'][i]['volume'] + (j-k) * (data_points[last_k_filled]['volume'] - c['data'][i]['volume']) / (j-last_k_filled)
							data_points[k]['market_cap'] = c['data'][i]['market_cap'] + (j-k) * (data_points[last_k_filled]['market_cap'] - c['data'][i]['market_cap']) / (j-last_k_filled)
						k -= 1
					break

		if data_points[-1]['price'] == 0:
			data_points = data_points[:-1]
		data_points = data_points[-hours_period:]
		
		c['data'] = data_points
		# print(json.dumps(data_points, default=str, indent=2))

	return data

def organize_data(c):
	res = {'id' : c[0]['id'], 'link': c[0]['link'], 'data': []}
	for d in c:
		res['data'].append({'created': d['created'], 'price': d['price'], 'volume': d['volume'], 'market_cap': d['market_cap']})
	return res

def get_data(hours_period):
	corrected_data = []
	for c in get_last_pulls_pancakeswap(hours_period):
		corrected_data.append(organize_data(c))
	# print(corrected_data)
	return fill_data_each_hour(corrected_data, hours_period)

def plot_regression(hourly_points):
	x = range(len(hourly_points))
	y = hourly_points
	slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
	regression_y = [intercept + slope*x for x in range(len(hourly_points))]
	average = (sum(hourly_points) / len(hourly_points))
	slope_relation_average_vol = 100 * slope / average
	diff_regression = [hourly_points[i] - regression_y[i] for i in range(len(hourly_points))]
	greater_than_regression = [x > 0 for x in diff_regression]
	
	# plt.plot(x, y, 'o', label='original data')
	# plt.plot(x, intercept + slope*x, 'r', label='fitted line')
	# plt.legend()
	# plt.show()

	return (slope_relation_average_vol, greater_than_regression, diff_regression, average)

def get_volatility_position(hourly_points):
	if not hourly_points or not len(hourly_points):
		return (0, 0)

	minimo = min(hourly_points)
	maximo = max(hourly_points)

	if minimo == 0 or minimo == maximo:
		return (0, 0)

	volatility = int(100 * maximo / minimo)
	position = int(100 * (hourly_points[-1] - minimo) / (maximo - minimo))

	return (volatility, position)

def alert_volume_regression_positive(hours_period=60, last_hours_above_regression=2):
	chosen = []
	for c in get_data(hours_period):
		# if len(chosen) > 3:
		# 	break
		# print(json.dumps(c, default=str, indent=2))
		hourly_vols = [x['volume'] for x in c['data']]
		hourly_price = [x['price'] for x in c['data']]

		volatility, position = get_volatility_position(hourly_price)
		vol_volatility, vol_position = get_volatility_position(hourly_vols)

		if volatility == 0 or vol_volatility == 0:
			continue
		
		slope_relation_average_vol, greater_than_regression, diff_regression, average = plot_regression(hourly_vols)
		slope_relation_average_price, greater_than_regression_price, diff_regression_price, average_price = plot_regression(hourly_price)
		
		price_ind = 100 * (slope_relation_average_price + 3 * diff_regression_price[-1] / average_price)
		vol_ind = 100 * (slope_relation_average_vol + 3 * diff_regression[-1] / average)

		if not math.isnan(price_ind) and not math.isnan(vol_ind) and position > 0: # and slope_relation_average_vol > 0.6: # and reduce((lambda x, y: x * y), greater_than_regression[-last_hours_above_regression:]):
			chosen.append({'link': c['link'], 'vol': int(vol_ind), 'price': int(price_ind), 
											'volatility': volatility, 'position': position, 'mc': round(c['data'][-1]['market_cap'] / 1000000, 2)})
	
	chosen.sort(key=lambda x: x['price'], reverse=True)
	# t = PrettyTable(['Link', 'volume', 'volatility', 'position', 'mc'])	
	# for g in chosen:
	# 	t.add_row([g['link'], f'{g["vol"]}', f'{g["volatility"]}', f'{g["position"]}', f'{g["mc"]}'])
	# print(t)

	return chosen


def good_ones(request):
	try:
			abrir_conexao()
			# run()
			# alert_growing_ps()
			g = alert_volume_regression_positive(85, 3)
			fechar_conexao()

			return HttpResponse(json.dumps(g), content_type="application/json")
	except:
			print("Erro aconteceu: ", traceback.format_exc())
			return HttpResponse(None)

