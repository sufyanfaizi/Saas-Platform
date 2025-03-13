from django.urls import path
from api.views import organization_views, user_views, project_views


urlpatterns = [
    # Subscription Management
    path('subscriptions/', organization_views.create_subscription_plan, name="create-subscription"),
    
    # Organization Management
    path('organizations/', organization_views.create_organization, name="create-organization"),
    path('organizations/<int:org_id>/subscriptions/', organization_views.change_subscription, name="change-subscription"),
    path('organizations/<int:org_id>/', organization_views.get_organization_details, name="get-organization-details"),

    # User Authentication & Management
    path('auth/register/', user_views.register_user, name="register-user"),
    path('auth/login/', user_views.login_user, name="login-user"),
    path('organizations/<int:org_id>/invite-user/', user_views.invite_user, name="invite-user"),
    path('organizations/<int:org_id>/remove-user/', user_views.remove_user, name="remove-user"),

    # Project Management
    path('projects/', project_views.create_project, name="create-project"),

    # Task Management
    path('tasks/', project_views.assign_task, name="assign-task"),
    path('tasks/', project_views.get_tasks, name="get-tasks"),  # Use query parameters instead of `/tasks/all/`
]
