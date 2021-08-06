from django.db import models

class Weapon(models.Model):
	weaponId = models.CharField(max_length=100)
	price = models.FloatField()
	weaponStars = models.IntegerField()
	weaponElement = models.CharField(max_length=100)
	stat1Element = models.CharField(max_length=100)
	stat1Value = models.IntegerField()
	stat2Element = models.CharField(max_length=100, blank=True, default='')
	stat2Value = models.IntegerField(blank=True, default=0)
	stat3Element = models.CharField(max_length=100, blank=True, default='')
	stat3Value = models.IntegerField(blank=True, default=0)


#  "idResults":[
#       "1178075",
#       "1150166",

	# "page":{
  #     "curPage":4,
  #     "curOffset":240,
  #     "total":86813,
  #     "pageSize":60,
  #     "numPages":1446
  #  }