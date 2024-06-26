import uuid

from datetime import timedelta
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.utils import timezone
from django.template.loader import render_to_string


from permission.apps import IsSuperAdmin, IsSupervisor

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
    AccountUpdateStatusSerializer,
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


class AccountListCreateView(generics.ListCreateAPIView):
    queryset = Account.objects.all()

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsSuperAdmin(), IsSupervisor()]
        return super().get_permissions()

    def send_password_email(self, recipient_email, password):
        subject = "Test Email"
        message = f"Your Password : {password}"
        recipient_list = [recipient_email]

        send_mail(
            subject=subject,
            message=message,
            from_email="hasbiasshidiq@gmail.com",  # From email
            recipient_list=recipient_list,
            fail_silently=False,
        )

        return

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

    def get(self, request, *args, **kwargs):
        self.serializer_class = AccountListSerializer
        return self.list(request, *args, **kwargs)


class AccountRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountDetailSerializer

    def delete(self, request, *args, **kwargs):
        self.permission_classes = [IsAuthenticated, IsSuperAdmin | IsSupervisor]
        return self.destroy(request, *args, **kwargs)


class AccountUpdateStatusView(mixins.UpdateModelMixin, generics.GenericAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountUpdateStatusSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def put(self, request, *args, **kwargs):
        user_id = kwargs.get("pk")
        try:
            account = Account.objects.get(id=user_id)
        except Account.DoesNotExist:
            return Response(
                {"error_code": AccountError.USER_DOES_NOT_EXIST},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AccountUpdateStatusSerializer(
            account, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AccountHasSetPasswordView(mixins.RetrieveModelMixin, generics.GenericAPIView):

    queryset = Account.objects.all()
    serializer_class = AccountDetailSerializer

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
    permission_classes = [AllowAny]

    def send_forgot_password_email(self, recipient_email, token, account_name):
        subject = "Test Forgot Password"
        recipient_list = [recipient_email]

        forgot_password_url = f"http://127.0.0.1:8000/{token}"

        context = {
            "account_name": account_name,
            "forgot_password_url": forgot_password_url,
        }

        send_mail(
            subject=subject,
            message="",
            from_email="hasbiasshidiq@gmail.com",  # From email
            recipient_list=recipient_list,
            fail_silently=False,
            html_message=render_to_string(
                template_name="forgot-password.html",
                context=context,
            ),
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

        self.send_forgot_password_email(user_email, token, account.name)

        AccountEmailToken.objects.create(
            account=account,
            token=token,
            status=AccountEmailTokenStatusEnum.active.value,
            expired_at=timezone.now() + timedelta(hours=24),
        )
        return Response({"status": "OK"}, status=status.HTTP_200_OK)


class ResetPasswordView(mixins.UpdateModelMixin, generics.GenericAPIView):

    queryset = Account.objects.all()
    serializer_class = AccountEmailTokenSerializer
    permission_classes = [AllowAny]

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
        except AccountEmailToken.DoesNotExist:
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


class ResetPasswordIsAvailableView(mixins.RetrieveModelMixin, generics.GenericAPIView):

    queryset = Account.objects.all()
    serializer_class = AccountEmailTokenSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):

        input_token = request.query_params.get("token", None)
        if input_token is None:
            return Response(
                "mising query param 'token'", status=status.HTTP_400_BAD_REQUEST
            )

        try:
            account_email_token = AccountEmailToken.objects.get(token=input_token)
        except AccountEmailToken.DoesNotExist:
            return Response({"is_available": False}, status=status.HTTP_200_OK)

        if account_email_token.status == AccountEmailTokenStatusEnum.inactive.value:
            return Response({"is_available": False}, status=status.HTTP_200_OK)

        if account_email_token.expired_at < timezone.now():
            if account_email_token.status == AccountEmailTokenStatusEnum.active.value:
                account_email_token.status = AccountEmailTokenStatusEnum.inactive.value
                account_email_token.save()
            return Response({"is_available": False}, status=status.HTTP_200_OK)

        return Response({"is_available": True}, status=status.HTTP_200_OK)
