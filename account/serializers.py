# accounts/serializers.py

from django.utils.crypto import get_random_string
from rest_framework import serializers
from .models import CustomUser
from django.urls import reverse
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'email',
            'password',
            'bio',
            'image'
        ]

        extra_kwargs = {
            "password": {
                "write_only": True
            }
        }

    def create(self, validated_data):
        user = CustomUser(**validated_data)

        user.set_password(validated_data['password'])

        user.verification_token = get_random_string(length=32)

        user.save()

        self.send_email(user=user)

        return user

    def send_email(self, user):

        # verification_link = f"http://127.0.0.1:8000/api/account/verify-email/{user.verification_token}/"

        # Prepare things for sending mail
        verification_link = self.context['request'].build_absolute_uri(
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

        return True


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class UserUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ["bio", "image"]

    def update(self, instance, validated_data):
        instance.bio = validated_data.get('bio', instance.bio)
        instance.image = validated_data.get('image', instance.image)
        instance.save()

        return instance

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    confirm_password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {
                    "confirm_password": "Passwords do not match."
                }
            )

        return data

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        write_only=True
    )

    new_password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    def validate(self, data):
        user = self.context["request"].user

        if not user.check_password(data["old_password"]):
            raise serializers.ValidationError(
                {
                    "old_password": "Old password is incorrect."
                }
            )

        if data["old_password"] == data["new_password"]:
            raise serializers.ValidationError(
                {
                    "new_password": "New password must be different from old password."
                }
            )

        return data