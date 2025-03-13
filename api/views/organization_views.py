from django.shortcuts import render
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

# Create your views here.
from ..serializers import *
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import extend_schema

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
    
