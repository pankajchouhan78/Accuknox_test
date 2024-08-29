from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from .models import Person


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ("name", "email", "password")

    def create(self, validated_data):
        password = validated_data.get("password", None)
        user = Person.objects.create(**validated_data)
        if password is not None:
            user.password = make_password(password)
            user.save()
        return user


class PersonSerializer(serializers.ModelSerializer):
    friends = serializers.StringRelatedField(many=True, read_only=True)
    sent_requests = serializers.StringRelatedField(many=True, read_only=True)
    received_requests = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="email"
    )

    class Meta:
        model = Person
        fields = (
            "id",
            "name",
            "email",
            "friends",
            "sent_requests",
            "received_requests",
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["friends_count"] = instance.friends.count()
        representation["sent_requests_count"] = instance.sent_requests.count()
        representation["received_requests_count"] = instance.received_requests.count()
        return representation


class SentRequestSerializer(serializers.Serializer):
    to_request = serializers.IntegerField()


class AcceptRequestSerializer(serializers.Serializer):
    accept_request = serializers.IntegerField()


class RejectRequestSerializer(serializers.Serializer):
    reject_request = serializers.IntegerField()


class SearchSerializer(serializers.Serializer):
    search = serializers.CharField(max_length=20)
