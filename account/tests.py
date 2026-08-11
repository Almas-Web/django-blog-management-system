from django.core import mail
from django.urls import reverse
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient

import pytest

from .models import CustomUser
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


@pytest.mark.django_db
@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
)
def test_user_signup():
    client = APIClient()

    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPassword123",
        "bio": "Test user bio",
    }

    response = client.post(
        reverse("signup"),
        data,
        format="json"
    )

    assert response.status_code == status.HTTP_201_CREATED

    user = CustomUser.objects.get(
        email="test@example.com"
    )

    assert user.username == "testuser"
    assert user.bio == "Test user bio"
    assert user.check_password("TestPassword123")
    assert not user.is_verified
    assert user.verification_token is not None

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["test@example.com"]


@pytest.mark.django_db
@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
)
def test_signup_with_duplicate_email():
    client = APIClient()

    data = {
        "username": "firstuser",
        "email": "duplicate@example.com",
        "password": "TestPassword123",
        "bio": "First user",
    }

    # First signup
    first_response = client.post(
        reverse("signup"),
        data,
        format="json"
    )

    assert first_response.status_code == status.HTTP_201_CREATED

    # Second signup with same email
    duplicate_data = {
        "username": "seconduser",
        "email": "duplicate@example.com",
        "password": "TestPassword456",
        "bio": "Second user",
    }

    second_response = client.post(
        reverse("signup"),
        duplicate_data,
        format="json"
    )

    assert second_response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_signup_with_missing_required_data():
    client = APIClient()

    data = {
        "username": "incompleteuser",
    }

    response = client.post(
        reverse("signup"),
        data,
        format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "password" in response.data


@pytest.mark.django_db
def test_user_login():
    client = APIClient()

    user = CustomUser.objects.create_user(
        username="loginuser",
        email="login@example.com",
        password="TestPassword123",
        is_verified=True,
    )

    data = {
        "email": "login@example.com",
        "password": "TestPassword123",
    }

    response = client.post(
        reverse("login"),
        data,
        format="json"
    )

    assert response.status_code == status.HTTP_200_OK

    assert "access_token" in response.data
    assert "refresh_token" in response.data


@pytest.mark.django_db
def test_user_login_with_invalid_credentials():
    client = APIClient()

    CustomUser.objects.create_user(
        username="loginuser2",
        email="login2@example.com",
        password="TestPassword123",
        is_verified=True,
    )

    data = {
        "email": "login2@example.com",
        "password": "WrongPassword123",
    }

    response = client.post(
        reverse("login"),
        data,
        format="json"
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data["details"] == "Invalid credentials"


@pytest.mark.django_db
def test_user_login_with_unverified_user():
    client = APIClient()

    CustomUser.objects.create_user(
        username="unverifieduser",
        email="unverified@example.com",
        password="TestPassword123",
        is_verified=False,
    )

    data = {
        "email": "unverified@example.com",
        "password": "TestPassword123",
    }

    response = client.post(
        reverse("login"),
        data,
        format="json"
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data["details"] == "Email is not verified yet!"


@pytest.mark.django_db
def test_verify_email():
    client = APIClient()

    user = CustomUser.objects.create_user(
        username="verifyuser",
        email="verify@example.com",
        password="TestPassword123",
        is_verified=False,
        verification_token="valid-token-123",
    )

    response = client.get(
        reverse(
            "verify_email",
            kwargs={"token": "valid-token-123"}
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["details"] == "Successfully verified!"

    user.refresh_from_db()

    assert user.is_verified is True
    assert user.verification_token is None


@pytest.mark.django_db
def test_verify_email_with_invalid_token():
    client = APIClient()

    response = client.get(
        reverse(
            "verify_email",
            kwargs={"token": "invalid-token-999"}
        )
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["details"] == "Invalid token"


@pytest.mark.django_db
def test_verify_email_already_verified():
    client = APIClient()

    user = CustomUser.objects.create_user(
        username="verifieduser",
        email="verified@example.com",
        password="TestPassword123",
        is_verified=True,
        verification_token="already-used-token",
    )

    response = client.get(
        reverse(
            "verify_email",
            kwargs={"token": "already-used-token"}
        )
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["details"] == "Email already verified!"


@pytest.mark.django_db
@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
)
def test_resend_verification_email():
    client = APIClient()

    user = CustomUser.objects.create_user(
        username="resenduser",
        email="resend@example.com",
        password="TestPassword123",
        is_verified=False,
        verification_token="old-token",
    )

    response = client.post(
        reverse("resend_verification"),
        {
            "email": "resend@example.com"
        },
        format="json"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["details"] == "Verfication email sent!"

    user.refresh_from_db()

    assert user.verification_token is not None
    assert user.verification_token != "old-token"

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["resend@example.com"]


@pytest.mark.django_db
def test_resend_verification_email_user_not_found():
    client = APIClient()

    response = client.post(
        reverse("resend_verification"),
        {
            "email": "notfound@example.com"
        },
        format="json"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.data["details"] == "User with this email doesn't exist!"


@pytest.mark.django_db
def test_resend_verification_email_already_verified():
    client = APIClient()

    CustomUser.objects.create_user(
        username="alreadyverified",
        email="alreadyverified@example.com",
        password="TestPassword123",
        is_verified=True,
        verification_token=None,
    )

    response = client.post(
        reverse("resend_verification"),
        {
            "email": "alreadyverified@example.com"
        },
        format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["details"] == "Email already verified!"


@pytest.mark.django_db
@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
)
def test_forgot_password_existing_user():
    client = APIClient()

    user = CustomUser.objects.create_user(
        username="forgotuser",
        email="forgot@example.com",
        password="OldPassword123",
    )

    response = client.post(
        reverse("forgot_password"),
        {
            "email": "forgot@example.com"
        },
        format="json"
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["details"] == (
        "Password reset link has been sent to your email."
    )

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["forgot@example.com"]

    assert "Reset Your Password" in mail.outbox[0].subject


@pytest.mark.django_db
def test_forgot_password_non_existing_user():
    client = APIClient()

    response = client.post(
        reverse("forgot_password"),
        {
            "email": "doesnotexist@example.com"
        },
        format="json"
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["details"] == (
        "If an account exists with this email, "
        "a password reset link has been sent."
    )

    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_reset_password():
    client = APIClient()

    user = CustomUser.objects.create_user(
        username="resetuser",
        email="reset@example.com",
        password="OldPassword123",
    )

    token_generator = PasswordResetTokenGenerator()

    uid = urlsafe_base64_encode(
        force_bytes(user.pk)
    )

    token = token_generator.make_token(user)

    data = {
        "new_password": "NewPassword123",
        "confirm_password": "NewPassword123",
    }

    response = client.post(
        reverse(
            "reset_password",
            kwargs={
                "uidb64": uid,
                "token": token,
            }
        ),
        data,
        format="json"
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["details"] == "Password reset successfully."

    user.refresh_from_db()

    assert user.check_password("NewPassword123")
    assert not user.check_password("OldPassword123")


@pytest.mark.django_db
def test_reset_password_invalid_uid():
    client = APIClient()

    response = client.post(
        reverse(
            "reset_password",
            kwargs={
                "uidb64": "invalid-uid",
                "token": "some-token",
            }
        ),
        {
            "new_password": "NewPassword123",
            "confirm_password": "NewPassword123",
        },
        format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["details"] == "Invalid password reset link."


@pytest.mark.django_db
def test_reset_password_invalid_token():
    client = APIClient()

    user = CustomUser.objects.create_user(
        username="invalidtokenuser",
        email="invalidtoken@example.com",
        password="OldPassword123",
    )

    uid = urlsafe_base64_encode(
        force_bytes(user.pk)
    )

    response = client.post(
        reverse(
            "reset_password",
            kwargs={
                "uidb64": uid,
                "token": "invalid-token-123",
            }
        ),
        {
            "new_password": "NewPassword123",
            "confirm_password": "NewPassword123",
        },
        format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["details"] == (
        "Invalid or expired password reset token."
    )


@pytest.mark.django_db
def test_reset_password_password_mismatch():
    client = APIClient()

    user = CustomUser.objects.create_user(
        username="mismatchuser",
        email="mismatch@example.com",
        password="OldPassword123",
    )

    token_generator = PasswordResetTokenGenerator()

    uid = urlsafe_base64_encode(
        force_bytes(user.pk)
    )

    token = token_generator.make_token(user)

    response = client.post(
        reverse(
            "reset_password",
            kwargs={
                "uidb64": uid,
                "token": token,
            }
        ),
        {
            "new_password": "NewPassword123",
            "confirm_password": "DifferentPassword123",
        },
        format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert "confirm_password" in response.data
    assert response.data["confirm_password"][0] == (
        "Passwords do not match."
    )


@pytest.mark.django_db
def test_change_password():
    client = APIClient()

    user = CustomUser.objects.create_user(
        username="changeuser",
        email="change@example.com",
        password="OldPassword123",
        is_verified=True,
    )

    client.force_authenticate(user=user)

    response = client.post(
        reverse("change_password"),
        {
            "old_password": "OldPassword123",
            "new_password": "NewPassword123",
        },
        format="json"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["details"] == "Password changed successfully."

    user.refresh_from_db()

    assert user.check_password("NewPassword123")
    assert not user.check_password("OldPassword123")


@pytest.mark.django_db
def test_change_password_wrong_old_password():
    client = APIClient()

    user = CustomUser.objects.create_user(
        username="wrongolduser",
        email="wrongold@example.com",
        password="OldPassword123",
        is_verified=True,
    )

    client.force_authenticate(user=user)

    response = client.post(
        reverse("change_password"),
        {
            "old_password": "WrongPassword123",
            "new_password": "NewPassword123",
        },
        format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert "old_password" in response.data
    assert response.data["old_password"][0] == (
        "Old password is incorrect."
    )


@pytest.mark.django_db
def test_change_password_same_password():
    client = APIClient()

    user = CustomUser.objects.create_user(
        username="samepassworduser",
        email="samepassword@example.com",
        password="OldPassword123",
        is_verified=True,
    )

    client.force_authenticate(user=user)

    response = client.post(
        reverse("change_password"),
        {
            "old_password": "OldPassword123",
            "new_password": "OldPassword123",
        },
        format="json"
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    assert "new_password" in response.data
    assert response.data["new_password"][0] == (
        "New password must be different from old password."
    )


@pytest.mark.django_db
def test_get_profile():
    client = APIClient()

    user = CustomUser.objects.create_user(
        username="profileuser",
        email="profile@example.com",
        password="TestPassword123",
        bio="My profile bio",
    )

    client.force_authenticate(user=user)

    response = client.get(
        reverse("profile")
    )

    assert response.status_code == status.HTTP_200_OK

    assert response.data["id"] == user.id
    assert response.data["username"] == "profileuser"
    assert response.data["email"] == "profile@example.com"
    assert response.data["bio"] == "My profile bio"


@pytest.mark.django_db
def test_update_profile():
    client = APIClient()

    user = CustomUser.objects.create_user(
        username="updateprofile",
        email="updateprofile@example.com",
        password="TestPassword123",
        bio="Old bio",
    )

    client.force_authenticate(user=user)

    response = client.patch(
        reverse("profile"),
        {
            "bio": "Updated bio",
        },
        format="json"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["bio"] == "Updated bio"

    user.refresh_from_db()

    assert user.bio == "Updated bio"


@pytest.mark.django_db
def test_profile_unauthorized():
    client = APIClient()

    response = client.get(
        reverse("profile")
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED