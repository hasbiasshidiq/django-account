from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from .models import Account, AccountStatusEnum
from .serializers import (
    AccountDetailSerializer,
    AccountListSerializer,
    SetInitialPasswordPayloadSerializer,
)
from rest_framework import mixins


class AccountListCreate(generics.ListCreateAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountListSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        request.data["status"] = AccountStatusEnum.inactive
        return self.create(request, *args, **kwargs)


class AccountRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountDetailSerializer
    permission_classes = [IsAuthenticated]


class AccountPasswordAvailabilityView(
    mixins.RetrieveModelMixin, generics.GenericAPIView
):

    queryset = Account.objects.all()
    serializer_class = AccountDetailSerializer
    permission_classes = (AllowAny,)

    def get(self, request):
        email = request.query_params.get("email", None)
        if email is None:
            return Response(
                {"error": "Email parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = Account.objects.get(email=email)
            if user.password:
                return Response({"has_password": True}, status=status.HTTP_200_OK)
            return Response({"has_password": False}, status=status.HTTP_200_OK)

        except Account.DoesNotExist:
            return Response(
                {"error": "User with this email does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )


class SetInitialPasswordView(mixins.UpdateModelMixin, generics.GenericAPIView):

    queryset = Account.objects.all()
    serializer_class = AccountDetailSerializer
    permission_classes = (AllowAny,)

    def put(self, request, *args, **kwargs):
        serializer = SetInitialPasswordPayloadSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        payload = serializer.data
        try:
            account = Account.objects.get(email=payload["email"])
        except Account.DoesNotExist:
            return Response(
                {"error": "User with this email does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if account.password:
            return Response(
                {"error": "User already has a password."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        account = Account.objects.get(id=account.id)

        # Update only the status field
        account.set_password(payload["password"])
        account.save()

        return Response("Password been set successfully", status=status.HTTP_200_OK)
