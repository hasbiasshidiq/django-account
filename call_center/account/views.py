from datetime import datetime, timedelta
import uuid

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone


from .const import AccountError, AccountEmailTokenError
from .models import (
    Account,
    AccountEmailToken,
    AccountEmailTokenStatusEnum,
    AccountStatusEnum,
)
from .serializers import (
    AccountCreateSerializer,
    AccountDetailSerializer,
    AccountEmailTokenSerializer,
    AccountListSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    SetInitialPasswordPayloadSerializer,
)
from django.contrib.auth.hashers import (
    make_password,
)
from django.core.mail import send_mail
from rest_framework import mixins
import random


class AccountListCreate(generics.ListCreateAPIView):
    queryset = Account.objects.all()
    permission_classes = [IsAuthenticated]

    def send_password_email(self, recipient_email, password):
        subject = "Test Email"
        message = f"Your password : {password}"
        recipient_list = [recipient_email]

        send_mail(
            subject,
            message,
            "hasbiasshidiq@gmail.com",  # From email
            recipient_list,
            fail_silently=False,
        )

        return

    def get(self, request, *args, **kwargs):
        self.serializer_class = AccountListSerializer
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        # Generate 5 random numbers
        random_numbers = "".join(str(random.randint(0, 9)) for _ in range(5))

        request.data["status"] = AccountStatusEnum.inactive
        request.data["password"] = make_password(random_numbers)

        self.serializer_class = AccountCreateSerializer
        created_obj = self.create(request, *args, **kwargs)

        # TODO : use background process
        self.send_password_email(request.data["email"], random_numbers)
        return created_obj


class AccountRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountDetailSerializer
    permission_classes = [IsAuthenticated]


class AccountHasSetPasswordView(mixins.RetrieveModelMixin, generics.GenericAPIView):

    queryset = Account.objects.all()
    serializer_class = AccountDetailSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        email = request.user.email
        try:
            user = Account.objects.get(email=email)
        except Account.DoesNotExist:
            return Response(
                {"error_code": AccountError.USER_DOES_NOT_EXIST},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {"has_set_password": user.has_set_password}, status=status.HTTP_200_OK
        )


class SetPasswordView(mixins.UpdateModelMixin, generics.GenericAPIView):

    queryset = Account.objects.all()
    serializer_class = AccountDetailSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        serializer = SetInitialPasswordPayloadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payload = serializer.data

        user_email = request.user.email
        try:
            account = Account.objects.get(email=user_email)
        except Account.DoesNotExist:
            return Response(
                {"error": "User with this email does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

        account = Account.objects.get(id=account.id)

        account.set_password(payload["password"])
        account.has_set_password = True
        account.save()

        return Response("Password been set successfully", status=status.HTTP_200_OK)


class ForgotPasswordView(mixins.CreateModelMixin, generics.GenericAPIView):

    queryset = Account.objects.all()
    serializer_class = AccountEmailTokenSerializer

    def send_forgot_password_email(self, recipient_email, token):
        subject = "Test Forgot Password"
        message = f"Your token : {token}"
        recipient_list = [recipient_email]

        send_mail(
            subject,
            message,
            "hasbiasshidiq@gmail.com",  # From email
            recipient_list,
            fail_silently=False,
        )

        return

    def post(self, request, *args, **kwargs):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payload = serializer.data

        user_email = payload["email"]
        try:
            account = Account.objects.get(email=user_email)
        except Account.DoesNotExist:
            return Response(
                {"error_code": AccountError.USER_DOES_NOT_EXIST},
                status=status.HTTP_404_NOT_FOUND,
            )

        token = uuid.uuid4()

        self.send_forgot_password_email(user_email, token)

        AccountEmailToken.objects.create(
            account=account,
            token=token,
            status=AccountEmailTokenStatusEnum.active.value,
            expired_at=datetime.now() + timedelta(hours=24),
        )
        return Response({"status": "OK"}, status=status.HTTP_200_OK)


class ResetPasswordView(mixins.UpdateModelMixin, generics.GenericAPIView):

    queryset = Account.objects.all()
    serializer_class = AccountEmailTokenSerializer

    def put(self, request, *args, **kwargs):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payload = serializer.data
        input_token = payload["token"]
        input_new_password = payload["new_password"]

        try:
            account_email_token = AccountEmailToken.objects.select_related(
                "account"
            ).get(token=input_token)
        except Account.DoesNotExist:
            return Response(
                {"error_code": AccountEmailTokenError.TOKEN_DOES_NOT_EXIST},
                status=status.HTTP_404_NOT_FOUND,
            )

        if account_email_token.status == AccountEmailTokenStatusEnum.inactive.value:
            return Response(
                {"error_code": AccountEmailTokenError.TOKEN_IS_EXPIRED},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if account_email_token.expired_at < timezone.now():
            if account_email_token.status == AccountEmailTokenStatusEnum.active.value:
                account_email_token.status = AccountEmailTokenStatusEnum.inactive.value
                account_email_token.save()
            return Response(
                {"error_code": AccountEmailTokenError.TOKEN_IS_EXPIRED},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        account = account_email_token.account
        account.set_password(input_new_password)
        account.save()

        account_email_token.status = AccountEmailTokenStatusEnum.inactive.value
        account_email_token.save()

        return Response({"status": "OK"}, status=status.HTTP_200_OK)
