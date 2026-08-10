
from django.urls import path

from .views import (
    UserSignUp,
    ResendVerificationEmail,
    VerifyEmail,
    UserLogin,
    RetrieveUpdateProfile,
    ForgotPassword,
    ResetPassword,
    ChangePassword,
)

from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path( 'signup/', UserSignUp.as_view(),name='signup'),

    path('verify-email/<str:token>/',VerifyEmail.as_view(),name='verify_email' ),

    path( 'resend-verification/',  ResendVerificationEmail.as_view(),name='resend_verification'
    ),

    path( 'login/',UserLogin.as_view(),name='login'),

    path('profile/',RetrieveUpdateProfile.as_view(),name='profile' ),

    path( 'token/refresh/', TokenRefreshView.as_view(), name='token_refresh'  ),
    path( 'forgot-password/',ForgotPassword.as_view(),
    name='forgot_password'),
    
    path(
    'reset-password/<uidb64>/<token>/',
    ResetPassword.as_view(),
    name='reset_password'),

    path(
    'change-password/',
    ChangePassword.as_view(),
    name='change_password'),
   
   
]
