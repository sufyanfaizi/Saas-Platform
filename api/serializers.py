from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Organization, SubscriptionPlan, Project, Task

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class ChangeSubscriptionSerializer(serializers.Serializer):
    subscription_plan = serializers.IntegerField(help_text="ID of the new Subscription Plan")


class UserRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, help_text="Username of the user")
    email = serializers.EmailField(help_text="Email of the user")
    password = serializers.CharField(write_only=True, help_text="Password of the user")
    is_admin = serializers.BooleanField(write_only=True, default=False, help_text="Indicates if the user should have admin privileges"
    )


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, help_text="Username of the user")
    password = serializers.CharField(required=True, write_only=True, help_text="Password of the user")


class InviteUserSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, help_text="Username of the user to invite")


class RemoveUserSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, help_text="Username of the user to remove")
