from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from account.models import Account
from rest_framework import serializers


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    email = serializers.EmailField()

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["email"] = user.email
        token["role"] = user.role

        return token


class TokenObtainPairRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128)
