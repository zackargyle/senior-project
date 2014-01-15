from api.models import *
from rest_framework import serializers


class GameSerializer(serializers.ModelSerializer):
	"""Serializes a Game object"""
	class Meta:
		model = Game


class GunSerializer(serializers.ModelSerializer):
	"""Serializes a Gun object"""
	class Meta:
		model = Gun


class PlayerSerializer(serializers.ModelSerializer):
    """Serializes an Player object"""
    class Meta:
        model = Player


class PlayerInstanceSerializer(serializers.ModelSerializer):
    """Serializes an PlayerInstance object"""
    class Meta:
        model = PlayerInstance
        depth = 1


class ShotSerializer(serializers.ModelSerializer):
    """Serializes an Shot object"""
    class Meta:
        model = Shot


class TeamSerializer(serializers.ModelSerializer):
    """Serializes an Team object"""
    class Meta:
        model = Team


