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

        return token

    # def validate(self, attrs):
    #     username = attrs.get("username")
    #     password = attrs.get("password")

    #     # Check if the account exists
    #     try:
    #         user = Account.objects.get(username=username)
    #     except Account.DoesNotExist:
    #         raise AuthenticationFailed({"message": "Account not found"})

    #     # Check if the password matches
    #     user = authenticate(username=username, password=password)
    #     if user is None:
    #         raise AuthenticationFailed({"message": "Account and password do not match"})

    #     # Everything is fine, proceed with the normal flow
    #     refresh = self.get_token(user)

    #     data = {
    #         "refresh": str(refresh),
    #         "access": str(refresh.access_token),
    #     }

    #     return data


class TokenObtainPairRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128)
