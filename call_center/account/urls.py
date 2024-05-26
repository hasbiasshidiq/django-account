from django.urls import path
from . import views

urlpatterns = [
    path("", views.AccountListCreateView.as_view(), name="account-list-create"),
    path(
        "<int:pk>/",
        views.AccountRetrieveUpdateDestroy.as_view(),
        name="account-detail",
    ),
    path(
        "<int:pk>/status",
        views.AccountUpdateStatusView.as_view(),
        name="account-update-status",
    ),
    path(
        "has-set-password",
        views.AccountHasSetPasswordView.as_view(),
        name="has-set-password",
    ),
    path("set-password", views.SetPasswordView.as_view(), name="set-password"),
    path("forgot-password", views.ForgotPasswordView.as_view(), name="forgot-password"),
    path("reset-password", views.ResetPasswordView.as_view(), name="reset-password"),
    path(
        "reset-password/is-available",
        views.ResetPasswordIsAvailableView.as_view(),
        name="reset-password-is-available",
    ),
]
