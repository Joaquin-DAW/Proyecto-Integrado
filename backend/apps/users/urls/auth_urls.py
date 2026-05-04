from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from apps.users import auth_views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('password-reset/', auth_views.PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset/confirm/', auth_views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]
