from django.db import models
from django.utils import timezone

class Crypto(models.Model):
	name = models.CharField(max_length=300)
	symbol = models.CharField(max_length=50)
	link = models.CharField(max_length=300)
	source_code = models.CharField(max_length=2000, null=True, blank=True)
	updated = models.DateTimeField(default=timezone.now, blank=True)

class CryptoWebsite(models.Model):
	crypto = models.ForeignKey(Crypto, on_delete=models.CASCADE)
	link = models.CharField(max_length=3000)

class Community(models.Model):
	host = models.CharField(max_length=2000)

class CryptoCommunity(models.Model):
	crypto = models.ForeignKey(Crypto, on_delete=models.CASCADE)
	community = models.ForeignKey(Community, on_delete=models.CASCADE)
	link = models.CharField(max_length=3000)

class Exchange(models.Model):
	name = models.CharField(max_length=2000)
	cmc_link = models.CharField(max_length=3000)

class CryptoExchange(models.Model):
	crypto = models.ForeignKey(Crypto, on_delete=models.CASCADE)
	exchange = models.ForeignKey(Exchange, on_delete=models.CASCADE)
	pair = models.CharField(max_length=1000)
	link = models.CharField(max_length=3000)

class Tag(models.Model):
	name = models.CharField(max_length=2000)
	link = models.CharField(max_length=3000, blank=True, null=True)	

class CryptoTag(models.Model):
	crypto = models.ForeignKey(Crypto, on_delete=models.CASCADE)
	tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

class Pull(models.Model):
	created = models.DateTimeField(default=timezone.now, blank=True)

class Data(models.Model):
	pull = models.ForeignKey(Pull, on_delete=models.CASCADE)
	crypto = models.ForeignKey(Crypto, on_delete=models.CASCADE)
	rank_num = models.IntegerField()
	price = models.FloatField()
	market_cap = models.FloatField()
	volume = models.FloatField()
	created = models.DateTimeField(default=timezone.now, blank=True)

class Delta(models.Model):
	crypto = models.ForeignKey(Crypto, on_delete=models.CASCADE)
	data1 = models.ForeignKey(Data, on_delete=models.CASCADE, related_name='fist_data')
	data2 = models.ForeignKey(Data, on_delete=models.CASCADE, related_name='second_data')
	hours_between = models.FloatField()
	rank_num = models.IntegerField()
	price = models.FloatField()
	market_cap = models.FloatField()
	volume = models.FloatField()
	created = models.DateTimeField(default=timezone.now, blank=True)
