from django.shortcuts import render
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework import viewsets , status

from api.models import UserOrganization
# Create your views here.
from ..serializers import *
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from drf_yasg import openapi
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema, OpenApiParameter
from ..permissions import IsAdminUser  # Import custom permission

@extend_schema(
    summary="Register User",
    request=UserRegistrationSerializer,  
    responses={201: UserRegistrationSerializer, 400: {"description": "Bad Request"}},
)
@api_view(['POST'])
def register_user(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = User.objects.create_user(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            is_staff = serializer.validated_data['isAdmin']
        )
        return Response(UserRegistrationSerializer(user).data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@extend_schema(
    summary="User Login",
    request=UserLoginSerializer,  # Use serializer for request validation
    responses={
        200: openapi.Schema(  # Define expected response schema
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description="JWT Refresh Token"),
                'access': openapi.Schema(type=openapi.TYPE_STRING, description="JWT Access Token"),
            },
        ),
        401: {"description": "Invalid credentials"},
    }
)
@api_view(['POST'])
def login_user(request):
    serializer = UserLoginSerializer(data=request.data)
    
    if serializer.is_valid():
        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]
        user = authenticate(username=username, password=password)
        
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }, status=status.HTTP_200_OK)
    
    return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)



@extend_schema(
    summary="Invite User to Organization",
    request=InviteUserSerializer,  # Use serializer for request validation
    responses={
        200: openapi.Schema(  # Define expected success response
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Success message confirming user invitation"
                )
            },
        ),
        403: {"description": "Only admins can invite users"},
        404: {"description": "User or Organization not found"},
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated,IsAdminUser])
def invite_user(request, org_id):
    serializer = InviteUserSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        try:
            user = User.objects.get(username=username)
            org = Organization.objects.get(id=org_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Organization.DoesNotExist:
            return Response({"error": "Organization not found"}, status=status.HTTP_404_NOT_FOUND)

        user_org = UserOrganization(user=user, organization=org)
        user_org.save()

        return Response({"message": f"User {username} invited successfully!"}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@extend_schema(
    summary="Remove User From Organization",
    request=RemoveUserSerializer,  
    responses={  
        200: {"description": "User removed successfully", "content": {"application/json": {"example": {"message": "User removed successfully"}}}},
        403: {"description": "Only admins can delete users"},
        404: {"description": "User not found"},
        400: {"description": "User is not part of this organization"},
    }
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated , IsAdminUser])
def remove_user(request, org_id):
    serializer = RemoveUserSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        user = get_object_or_404(User, username=username)

        user_org = UserOrganization.objects.filter(user=user, organization_id=org_id)
        
        if not user_org.exists():
            return Response({"error": "User is not part of this organization"}, status=status.HTTP_400_BAD_REQUEST)
        
        user_org.delete()
        return Response({"message": "User removed successfully"}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
