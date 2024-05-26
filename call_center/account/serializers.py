from rest_framework import serializers
from .models import Account, AccountEmailToken


###################################
######## ACCOUNT SERILIZER ########
###################################
class AccountDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["id", "name", "email", "role", "status", "created_at"]


class AccountListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["id", "name", "email", "role", "status"]


class AccountCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["id", "name", "email", "password", "role", "status"]

    def to_representation(self, instance):
        # Call the parent class's to_representation() method
        data = super().to_representation(instance)
        # Exclude the 'password' field from the serialized data
        data.pop("password", None)
        return data


class AccountUpdateStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["status"]


###############################################
######## ACCOUNT EMAIL TOKEN SERILIZER ########
###############################################
class AccountEmailTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountEmailToken
        fields = ["id", "account", "token", "expired_at"]


###################################
######## REQUEST SERILIZER ########
###################################


# class to parse endpoint SetInitialPassword
class SetInitialPasswordPayloadSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=128)


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    new_password = serializers.CharField(max_length=128)
