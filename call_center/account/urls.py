from django.urls import path
from . import views

urlpatterns = [
    path("", views.AccountListCreate.as_view(), name="account-list"),
    path(
        "<int:pk>/",
        views.AccountRetrieveUpdateDestroy.as_view(),
        name="account-detail",
    ),
    path(
        "password-availability/",
        views.AccountPasswordAvailabilityView.as_view(),
        name="password-availability",
    ),
    path(
        "set-password",
        views.SetInitialPasswordView.as_view(),
        name="set-password",
    ),
]
