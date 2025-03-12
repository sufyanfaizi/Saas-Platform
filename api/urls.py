from django.urls import path
from .views import *

urlpatterns = [
    path('subscription/', create_subscription_plan),
    path('organization/', create_organization),
    path('organization/<int:org_id>/change-subscription/', change_subscription),
    path('organization/<int:org_id>/', get_organization_details),
    path('register/', register_user),
    path('login/', login_user),
    path('organization/<int:org_id>/invite/', invite_user),
    path('organization/<int:org_id>/removeuser/', remove_user),
    path('projects/', create_project),
    path('tasks/', assign_task),
    path('tasks/all/', get_tasks),
]