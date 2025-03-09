# accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Wallet, Transaction
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username", "password", "first_name", "last_name"]
        extra_kwargs = {
            "password": {"write_only": True},
            "username": {"required": False},
        }

    def create(self, validated_data):
        if "username" not in validated_data:
            # Set username to email if not provided
            validated_data["username"] = validated_data["email"]

        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "date_joined",
            "last_login",
        ]
        read_only_fields = ["id", "email", "date_joined", "last_login"]
        extra_kwargs = {
            "username": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
        }


class WalletSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Wallet
        fields = ["id", "user_email", "username", "balance", "created_at", "updated_at"]
        read_only_fields = [
            "id",
            "user_email",
            "username",
            "balance",
            "created_at",
            "updated_at",
        ]


class TransactionSerializer(serializers.ModelSerializer):
    from_email = serializers.EmailField(
        source="from_wallet.user.email", read_only=True, allow_null=True
    )
    to_email = serializers.EmailField(
        source="to_wallet.user.email", read_only=True, allow_null=True
    )
    transaction_type_display = serializers.CharField(
        source="get_transaction_type_display", read_only=True
    )

    class Meta:
        model = Transaction
        fields = [
            "id",
            "transaction_id",
            "from_wallet",
            "to_wallet",
            "from_email",
            "to_email",
            "amount",
            "transaction_type",
            "transaction_type_display",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "transaction_id",
            "from_wallet",
            "to_wallet",
            "amount",
            "transaction_type",
            "created_at",
        ]


class DepositSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        return value


class WithdrawSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        return value


class TransferSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    recipient_email = serializers.EmailField()

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        return value


# for login process, replaces the default username field with email
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = "email"
