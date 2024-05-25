from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate

from account.const import AccountError, AuthError
from account.models import Account
from .serializers import (
    CustomTokenObtainPairSerializer,
    TokenObtainPairRequestSerializer,
)


# Create your views here.
class CustomTokenObtainPairView(TokenObtainPairView):

    def post(self, request, *args, **kwargs):
        # validate request payload
        serializer = TokenObtainPairRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = request.data["email"]
        password = request.data["password"]

        # Check if the account exists
        try:
            Account.objects.get(email=email)
        except Account.DoesNotExist:
            return Response(
                {"error_code": AccountError.USER_DOES_NOT_EXIST},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if the password matches
        user = authenticate(email=email, password=password)
        if user is None:
            return Response(
                {"error_code": AuthError.PASSWORD_DOES_NOT_MATCH},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Everything is fine, proceed with the normal flow
        refresh = CustomTokenObtainPairSerializer.get_token(user)

        data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

        return Response(data, status=status.HTTP_200_OK)
