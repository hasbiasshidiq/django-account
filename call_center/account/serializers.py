from rest_framework import serializers
from .models import Account
from django.utils.translation import gettext_lazy as _


class AccountDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["id", "name", "email", "role", "status", "created_at"]


class AccountListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["id", "name", "email", "role", "status"]


class SetInitialPasswordPayloadSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128)
