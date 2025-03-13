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