from rest_framework import serializers
from . import models

class WeaponSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Weapon
        fields = '__all__'
			
class CharacterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Character
        fields = '__all__'

class PersonalAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PersonalAccount
        fields = '__all__'

class XpTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.XpTable
        fields = '__all__'
				