from django.db import models
from django.utils import timezone

class Weapon(models.Model):
	weaponId = models.CharField(max_length=100)
	seller = models.CharField(max_length=200)
	price = models.FloatField()
	weaponStars = models.IntegerField()
	weaponElement = models.CharField(max_length=100)
	stat1Element = models.CharField(max_length=100)
	stat1Value = models.IntegerField()
	stat2Element = models.CharField(max_length=100, blank=True, default='')
	stat2Value = models.IntegerField(blank=True, default=0)
	stat3Element = models.CharField(max_length=100, blank=True, default='')
	stat3Value = models.IntegerField(blank=True, default=0)
	power = models.FloatField()
	powerPerPrice = models.FloatField()
	updated = models.DateTimeField(default=timezone.now, blank=True)

	class Meta:
		ordering = ['-powerPerPrice']

class Character(models.Model):
	charId = models.CharField(max_length=100)
	seller = models.CharField(max_length=200)
	price = models.FloatField()
	xp = models.IntegerField()
	level = models.IntegerField()
	power = models.IntegerField()
	element = models.CharField(max_length=100)
	powerPerPrice = models.FloatField()
	updated = models.DateTimeField(default=timezone.now, blank=True)

	class Meta:
		ordering = ['-powerPerPrice']

class Banned(models.Model):
	address = models.CharField(max_length=200)