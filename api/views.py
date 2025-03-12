from django.shortcuts import render
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework import viewsets , status

from api.models import UserOrganization
# Create your views here.
from .serializers import *
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from drf_yasg import openapi
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema, OpenApiParameter

@extend_schema(
    summary="Create Subscription Plan",
    request=SubscriptionPlanSerializer,  
    responses={201: SubscriptionPlanSerializer, 400: "Bad Request"},
)
@api_view(['POST']) 
def create_subscription_plan(request):
    subscription_plan_serializer = SubscriptionPlanSerializer(data=request.data)
    if subscription_plan_serializer.is_valid():
        subscription_plan_serializer.save()
        return Response(subscription_plan_serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(subscription_plan_serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@extend_schema(
    summary="Create Organization and Assign",
    request=OrganizationSerializer,     
    responses={201: OrganizationSerializer, 400: "Bad Request"},
)
@api_view(['POST'])  
def create_organization(request):
    organization_serializer = OrganizationSerializer(data=request.data)
    if organization_serializer.is_valid():
        organization_serializer.save()
        return Response(organization_serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(organization_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Change Subscription Plan",
    request=ChangeSubscriptionSerializer, 
    responses={
        200: {"description": "Subscription updated successfully!"},
        404: {"description": "Organization or Subscription Plan not found"},
    }
)
@api_view(['PATCH'])
def change_subscription(request, org_id):
    try:
        org = Organization.objects.get(id=org_id)
        serializer = ChangeSubscriptionSerializer(data = request.data)
        if serializer.is_valid():
            plan = SubscriptionPlan.objects.get(id=serializer.validated_data['subscription_plan'])
            org.subscription_plan = plan
            org.save()
            return Response({"message": "Subscription updated successfully!"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Organization.DoesNotExist:
        return Response({"error": "Organization not found"}, status=404)
    except SubscriptionPlan.DoesNotExist:
        return Response({"error": "Subscription plan not found"}, status=404)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_organization_details(request, org_id):
    try:
        if request.user.is_staff:
            org = Organization.objects.get(id=org_id)
            serializer = OrganizationSerializer(org)
            return Response(serializer.data)
        return Response({"error": "Unauthorized"}, status=403)
    except Organization.DoesNotExist:
        return Response({"error": "Organization not found"}, status=404)
    

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
            password=serializer.validated_data['password']
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
@permission_classes([IsAuthenticated])
def invite_user(request, org_id):
    if not request.user.is_staff:
        return Response({"error": "Only admins can invite users"}, status=status.HTTP_403_FORBIDDEN)

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
@permission_classes([IsAuthenticated])
def remove_user(request, org_id):
    if not request.user.is_staff:
        return Response({"error": "Only admins can delete users"}, status=status.HTTP_403_FORBIDDEN)

    serializer = RemoveUserSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        user = get_object_or_404(User, username=username)

        user_org = UserOrganization.objects.filter(user=user, organization_id=org_id)
        
        if not user_org.exists():
            return Response({"error": "User is not part of this organization"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Remove user from the organization
        user_org.delete()
        return Response({"message": "User removed successfully"}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    summary="Create Project",
    request=ProjectSerializer,  
    responses={201: ProjectSerializer, 400: "Bad Request"},
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_project(request):
    serializer = ProjectSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Assign Task",
    request=TaskSerializer,  
    responses={201: TaskSerializer, 400: "Bad Request"},
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_task(request):
    serializer = TaskSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Get Tasks",
    description="Retrieve tasks with optional filtering by status, project ID, or due date.",
    parameters=[
        OpenApiParameter(
            name="status",
            location=OpenApiParameter.QUERY,
            description="Filter by task status",
            required=False,
            type=str,
            enum=["pending", "in_progress", "completed", "cancelled"]
        ),
        OpenApiParameter(
            name="project",
            location=OpenApiParameter.QUERY,
            description="Filter by project ID",
            required=False,
            type=int
        ),
        OpenApiParameter(
            name="due_date",
            location=OpenApiParameter.QUERY,
            description="Filter by due date (YYYY-MM-DD)",
            required=False,
            type=str  
        ),
    ],
    responses={200: TaskSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_tasks(request):
    tasks = Task.objects.all()
    status_filter = request.GET.get("status")
    project_filter = request.GET.get("project")
    due_date_filter = request.GET.get("due_date")

    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if project_filter:
        tasks = tasks.filter(project_id=project_filter)
    if due_date_filter:
        tasks = tasks.filter(due_date=due_date_filter)

    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)