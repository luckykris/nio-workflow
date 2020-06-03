"""cmdb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework import routers
from workflow.wfapp import views
from rest_framework_extensions.routers import ExtendedSimpleRouter
# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
#     TokenVerifyView,
# )

router = routers.DefaultRouter()
router.register(r'step_define', views.StepDefineViewSet)
router.register(r'workflow_template', views.WorkflowTemplateViewSet)


urlpatterns = [
    path(r'api/token-auth/', views.CustomAuthToken.as_view()),
    #
    # jwt
    # path(r'api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path(r'api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path(r'api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    #
    path('v1/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('admin/', admin.site.urls),
    path(r'', TemplateView.as_view(template_name="index.html")),
]
