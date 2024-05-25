from django.urls import path
from . import views

urlpatterns = [
    path("", views.AccountListCreate.as_view(), name="account-list"),
    path(
        "<int:pk>/", views.AccountRetrieveUpdateDestroy.as_view(), name="account-detail"
    ),
    path(
        "has-set-password",
        views.AccountHasSetPasswordView.as_view(),
        name="has-set-password",
    ),
    path("set-password", views.SetPasswordView.as_view(), name="set-password"),
    path("forgot-password", views.ForgotPasswordView.as_view(), name="forgot-password"),
    path("reset-password", views.ResetPasswordView.as_view(), name="reset-password"),
]
