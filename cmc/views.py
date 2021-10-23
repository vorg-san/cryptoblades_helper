from datetime import datetime, timedelta
from django.utils import timezone as djangotimezone
from pytz import timezone
from django.shortcuts import render
import requests
import bs4
from bs4 import BeautifulSoup
from time import sleep
import time
from random import randrange
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from . import models
import re
from selenium.common.exceptions import StaleElementReferenceException

def convert_price_to_num(text):
	return text.strip().replace('$', '').replace(',','').replace('<','')



def wait_random(min=1, max=5):
	sleep(randrange(min, max))

class cmc:
	def __init__(self, browser, start_page=1, previous_pull=None, create_pull=True):
		self.previous_pull = previous_pull
		self.browser = browser
		
		if create_pull:
			self.browser.get(f'https://coinmarketcap.com?page={start_page}')
			self._close_cookie()
			self.scroll_until_end()

			self.pull = models.Pull()
			self.pull.save()

	def close(self):
		self.browser.close()
		self.browser.quit()

	def _close_cookie(self):
		cookie = self.browser.find_elements_by_css_selector('div.cmc-cookie-policy-banner__close')
			
		if len(cookie):
			cookie[0].click()

	def scroll_until_end(self): 
		SCROLL_PAUSE_TIME = 0.5

		max_height = self.browser.execute_script("return document.body.scrollHeight")
		window_height = self.browser.execute_script("return window.innerHeight")
		current_height = window_height
		while current_height < max_height:
			self.browser.execute_script(f'window.scrollTo(0, {current_height});')
			current_height += window_height
			sleep(SCROLL_PAUSE_TIME)


	def infinite_scroll(self): 
		SCROLL_PAUSE_TIME = 0.5

		# Get scroll height
		last_height = self.browser.execute_script("return document.body.scrollHeight")

		while True:
			# Scroll down to bottom
			self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

			# Wait to load page
			sleep(SCROLL_PAUSE_TIME)

			# Calculate new scroll height and compare with last scroll height
			new_height = self.browser.execute_script("return document.body.scrollHeight")
			if new_height == last_height:
				break
			last_height = new_height

	def rank_page(self, count=0):
		trs = self.browser.find_elements_by_css_selector(".cmc-table tr")
		
		for tr in trs:
			s = BeautifulSoup(tr.get_attribute("innerHTML"), 'html.parser')
			cols = s.find_all('td')

			if len(cols) > 3:
				count += 1
				symbol_sup = cols[2].find('a', class_='cmc-link')

				link = symbol_sup['href']
				re_search = re.search('/currencies/(.*)/', link, re.IGNORECASE)
				if re_search:
						link = re_search.group(1)
				
				if not symbol_sup.find('div'):
					name = symbol_sup.find_all('span')[1].text
				else:
					name = symbol_sup.find('div').find('div').find('p').text

				if symbol_sup.find('p', class_='coin-item-symbol'):
					symbol = symbol_sup.find('p', class_='coin-item-symbol').text
				else:
					symbol = symbol_sup.find('span', class_='crypto-symbol').text

				price = convert_price_to_num(cols[3].text)
				market_cap = 0
				volume = 0

				if len(cols) > 7:
					if cols[6].find('span'):
						market_cap = convert_price_to_num(cols[6].find('span').find_next_sibling('span').text)
					if cols[7].find('a', class_='cmc-link'):
						volume = convert_price_to_num(cols[7].find('a', class_='cmc-link').text)
				
				try:
					c = models.Crypto.objects.get(name=name, symbol=symbol, link=link)
				except models.Crypto.DoesNotExist:
					c = models.Crypto()
					c.name = name
					c.symbol = symbol
					c.link = link
					c.save()

				try:
					cd = models.Data.objects.get(pull=self.pull, crypto=c)
				except models.Data.DoesNotExist:
					cd = models.Data()
					cd.pull = self.pull
					cd.crypto = c
					cd.rank_num = count
					cd.price = float(price)
					cd.market_cap = float(market_cap)
					cd.volume = float(volume)
					cd.save()

					try:
						previous_data = models.Data.objects.get(pull=self.previous_pull, crypto=c)
						
						d = models.Delta()
						d.crypto = c
						d.data1 = previous_data
						d.data2 = cd
						d.hours_between = round((cd.created - previous_data.created).total_seconds() / 3600, 1)
						d.rank_num = previous_data.rank_num - cd.rank_num
						d.price = round(100 * (cd.price - previous_data.price)/previous_data.price, 2) if previous_data.price != 0 else 0
						d.market_cap = round(100 * (cd.market_cap - previous_data.market_cap)/previous_data.market_cap, 2) if previous_data.market_cap != 0 else 0
						d.volume = round(100 * (cd.volume - previous_data.volume)/previous_data.volume, 2) if previous_data.volume != 0 else 0
						d.save()
					except models.Data.DoesNotExist:
						print('new crypto!', c.symbol, c.name, c.link)

		return count

	def next_page(self):
		next_link = self.browser.find_elements_by_css_selector("ul.pagination li.next a")

		if len(next_link):
			has_next = 'disabled' not in next_link[-1].find_element_by_xpath('..').get_attribute("class")
			
			if has_next:
				next_link[-1].click()
				self.scroll_until_end()

			return has_next
		return False
	
	def _action_move_to_logo(self, action):
		logo = self.browser.find_elements_by_xpath("//a[contains(@class,'cmc-logo-link')]")
		action.move_to_element(logo[0]).perform()

	def _save_community(self, crypto, link):
		href = link.get_attribute('href')
		re_search = re.search('.*?//(.*?)/.*', href, re.IGNORECASE)
		if re_search:
			host = re_search.group(1)
			
			try:
				c = models.Community.objects.get(host=host)
			except models.Community.DoesNotExist:
				c = models.Community()
				c.host = host
				c.save()

			try:
				cc = models.CryptoCommunity.objects.get(crypto=crypto, community=c, link=href)
			except models.CryptoCommunity.DoesNotExist:
				cc = models.CryptoCommunity()
				cc.crypto = crypto
				cc.community = c
				cc.link = href
				cc.save()

	def _get_community(self, crypto, action): 
		com = self.browser.find_elements_by_xpath("//div[contains(@class,'buttonName')][contains(.,'Community')]")
		
		if len(com):
			com = com[0].find_element_by_xpath('..')

			if com.get_attribute('href'):
				self._save_community(crypto, com)
			else:
				action.move_to_element(com).perform()
				popup_links = self.browser.find_elements_by_xpath("//div[contains(@class,'tippy-content')]//ul//li//a")
				for link in popup_links:
					self._save_community(crypto, link)					

				self._action_move_to_logo(action)

	def _get_website(self, crypto, action):
		com = self.browser.find_elements_by_xpath("//div[contains(@class,'buttonName')][contains(.,'Website')]")
		if len(com):
			action.move_to_element(com[0].find_element_by_xpath('..')).perform()
			popup_links = self.browser.find_elements_by_xpath("//div[contains(@class,'tippy-content')]//ul//li//a")
		else:
			popup_links = self.browser.find_elements_by_xpath("//ul[contains(@class,'content')]//li//a")
			if len(popup_links):
				popup_links = popup_links[:1]
			else:
				popup_links = []
			
		for link in popup_links:
			href = link.get_attribute('href')
			
			try:
				cw = models.CryptoWebsite.objects.get(crypto=crypto, link=href)
			except models.CryptoWebsite.DoesNotExist:
				cw = models.CryptoWebsite()
				cw.crypto = crypto
				cw.link = href
				cw.save()
		
		if len(com):
			self._action_move_to_logo(action)

	def _get_source_code(self, crypto):
		com = self.browser.find_elements_by_xpath("//div[contains(@class,'buttonName')][contains(.,'Source code')]")
		if len(com):
			link = com[0].find_element_by_xpath('..')
			href = link.get_attribute('href')
			
			if href:
				crypto.source_code = href
				crypto.save()

	def _get_tags(self, crypto):
		view_all = self.browser.find_elements_by_xpath("//li[contains(@class,'tagBadge')][contains(@class,'viewAll')]")
		if len(view_all):
			view_all[0].click()
			
		elements = self.browser.find_elements_by_xpath("//div[contains(@class,'tagBadge')]")
		for e in elements:
			link = e.find_element_by_xpath('..')
			href = link.get_attribute('href')
			name = e.text

			if name:
				try:
					t = models.Tag.objects.get(name=name)

					if not t.link and href:
						t.link = href
						t.save()
				except models.Tag.DoesNotExist:
					t = models.Tag()
					t.name = name
					t.link = href
					t.save()

				try:
					ct = models.CryptoTag.objects.get(crypto=crypto, tag=t)
				except models.CryptoTag.DoesNotExist:
					ct = models.CryptoTag() 
					ct.crypto = crypto
					ct.tag = t
					ct.save()

	def _get_markets(self, crypto):
		self.browser.get(f'https://coinmarketcap.com/currencies/{crypto.link}/markets/')
		# self._close_cookie()
		wait_random(1,2)
		self.scroll_until_end()
		elements = self.browser.find_elements_by_xpath("//table[contains(@class,'cmc-table')]//tbody//tr")
		for tr in elements:
			try:
				a = tr.find_elements_by_xpath(".//td[2]//a")

				if len(a):
					a = a[0]
					cmc_link = a.get_attribute('href')
					name = a.text

					try:
						e = models.Exchange.objects.get(name=name)
					except models.Exchange.DoesNotExist:
						e = models.Exchange() 
						e.name = name
						e.cmc_link = cmc_link
						e.save()

					a = tr.find_elements_by_xpath(".//td[3]//a")
					if len(a):
						a = a[0]
						link = a.get_attribute('href')
						pair = a.text

						try:
							ce = models.CryptoExchange.objects.get(crypto=crypto, exchange=e, pair=pair, link=link)
						except models.CryptoExchange.DoesNotExist:
							ce = models.CryptoExchange() 
							ce.crypto = crypto
							ce.exchange = e
							ce.pair = pair
							ce.link = link
							ce.save()
			except StaleElementReferenceException as e:
				print(e)

	def crypto_page(self, crypto, tz):
		self.browser.get(f'https://coinmarketcap.com/currencies/{crypto.link}/')
		self._close_cookie()
		action = ActionChains(self.browser)
		
		self._get_community(crypto, action)
		self._get_website(crypto, action)
		self._get_source_code(crypto)
		self._get_tags(crypto)
		self._get_markets(crypto) 

		crypto.updated = djangotimezone.now()
		crypto.save()

 
def run():	 
	while True:
		tz = timezone('America/Sao_Paulo')
		should_pull = True
		p = None

		try:
			p = models.Pull.objects.latest('id')
			should_pull = p.created.astimezone(tz).isoformat() < (datetime.now(tz) - timedelta(hours=1)).isoformat()
		except models.Crypto.DoesNotExist:
			pass
		
		print(datetime.now(tz).isoformat(), f'should_pull: {should_pull}')

		if should_pull:
			erro = False

			try:
				browser = webdriver.Firefox()
				browser.implicitly_wait(3)
				page = cmc(browser, 1, p)
			except Exception as e:
				print(f'Erro ocorreu! {e}')
				erro = True
				
			if not erro:
				count = 0
				while True:
					count = page.rank_page(count)
					if not page.next_page():
						break

				page.close()
		else:
		  pass
			# browser = webdriver.Firefox()
			# browser.implicitly_wait(2)
			# page = cmc(browser, 1, p, create_pull=False)
			# max_per_turn = 120
			
			# for crypto in models.Crypto.objects.order_by('updated'):
			# 	page.crypto_page(crypto, tz)
			# 	max_per_turn -= 1

			# 	if max_per_turn == 0:
			# 		page.close()
			# 		break

			# 	wait_random(2, 4)

		wait_random(1*60, 3*60)
	
# https://coinmarketcap.com/historical/

run()