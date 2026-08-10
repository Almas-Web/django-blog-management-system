
from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from django.utils.http import (
    urlsafe_base64_encode,
    urlsafe_base64_decode,
)

from .serializers import (
    UserSerializer,
    UserLoginSerializer,
    UserUpdateSerializer, 
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    ChangePasswordSerializer,
)
from rest_framework.permissions import IsAuthenticated

from .models import CustomUser

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.urls import reverse

from rest_framework_simplejwt.tokens import RefreshToken

# Will implement later
# from django.shortcuts import render
# from rest_framework.permissions import IsAuthenticated


class UserSignUp(generics.CreateAPIView):
    serializer_class = UserSerializer


class VerifyEmail(generics.GenericAPIView):
    swagger_fake_view = True  # Bypass schema generation for this view

    def get(self, request, token):
        user = CustomUser.objects.filter(
            verification_token=token
        ).first()

        if user:
            if user.is_verified:
                return Response({
                    "details": "Email already verified!",
                }, status=status.HTTP_400_BAD_REQUEST)

            user.is_verified = True
            user.verification_token = None
            user.save()

            return Response({
                "details": "Successfully verified!",
            }, status=status.HTTP_200_OK)

        return Response({
            "details": "Invalid token",
        }, status=status.HTTP_400_BAD_REQUEST)


class ResendVerificationEmail(generics.GenericAPIView):
    swagger_fake_view = True  # Bypass schema generation for this view

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')

        if email:
            user = CustomUser.objects.filter(email=email).first()

            if not user:
                return Response({
                    "details": "User with this email doesn't exist!",
                }, status=status.HTTP_404_NOT_FOUND)

            if user.is_verified:
                return Response({
                    "details": "Email already verified!",
                }, status=status.HTTP_400_BAD_REQUEST)

            user.verification_token = get_random_string(length=32)
            user.save()

            # Prepare things for sending mail
            verification_link = request.build_absolute_uri(
                reverse(
                    viewname='verify_email',
                    kwargs={
                        'token': user.verification_token
                    }
                ),
            )

            # Render the email template
            subject = 'Verify you email'

            html_content = render_to_string(
                'emails/verification_email.html',
                {
                    "user": user.username,
                    "verification_link": verification_link
                }
            )

            # Create an email message
            email = EmailMultiAlternatives(
                subject,
                "This is a plain text version of the email",
                "from@example.com",
                [user.email]
            )

            email.attach_alternative(
                html_content,
                "text/html"
            )

            email.send(fail_silently=False)

            return Response({
                "details": "Verfication email sent!",
            }, status=status.HTTP_200_OK)


class UserLogin(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = CustomUser.objects.filter(email=email).first()

        if user:
            matched_password = user.check_password(password)

            if matched_password:

                if not user.is_verified:
                    return Response({
                        "details": "Email is not verified yet!",
                    }, status=status.HTTP_401_UNAUTHORIZED)

                refresh = RefreshToken.for_user(user)

                return Response({
                    "refresh_token": str(refresh),
                    "access_token": str(refresh.access_token)
                })

        return Response({
            "details": "Invalid credentials",
        }, status=status.HTTP_401_UNAUTHORIZED)


class RetrieveUpdateProfile(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer

        return UserSerializer

class ForgotPassword(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        user = CustomUser.objects.filter(email=email).first()

        if not user:
            return Response(
                {
                    "details": "If an account exists with this email, "
                               "a password reset link has been sent."
                },
                status=status.HTTP_200_OK
            )

        uid = urlsafe_base64_encode(
            force_bytes(user.pk)
        )

        token = PasswordResetTokenGenerator().make_token(user)

        reset_link = request.build_absolute_uri(
            reverse(
                "reset_password",
                kwargs={
                    "uidb64": uid,
                    "token": token,
                }
            )
        )

        subject = "Reset Your Password"

        html_content = render_to_string(
            "emails/password_reset_email.html",
            {
                "user": user.username,
                "reset_link": reset_link,
            }
        )

        email = EmailMultiAlternatives(
            subject,
            f"Reset your password using this link:\n\n{reset_link}",
            "from@example.com",
            [user.email]
        )

        email.attach_alternative(
            html_content,
            "text/html"
        )

        email.send(fail_silently=False)

        return Response(
            {
                "details": "Password reset link has been sent to your email."
            },
            status=status.HTTP_200_OK
        )

class ResetPassword(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer

    def post(self, request, uidb64, token):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            uid = force_str(
                urlsafe_base64_decode(uidb64)
            )

            user = CustomUser.objects.get(pk=uid)

        except (
            TypeError,
            ValueError,
            OverflowError,
            CustomUser.DoesNotExist
        ):
            return Response(
                {
                    "details": "Invalid password reset link."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        token_generator = PasswordResetTokenGenerator()

        if not token_generator.check_token(user, token):
            return Response(
                {
                    "details": "Invalid or expired password reset token."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(
            serializer.validated_data["new_password"]
        )

        user.save()

        return Response(
            {
                "details": "Password reset successfully."
            },
            status=status.HTTP_200_OK
        )

class ChangePassword(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = self.get_serializer(
            data=request.data,
            context={"request": request}
        )

        serializer.is_valid(raise_exception=True)

        user = request.user

        user.set_password(
            serializer.validated_data["new_password"]
        )

        user.save()

        return Response(
            {
                "details": "Password changed successfully."
            },
            status=status.HTTP_200_OK
        )