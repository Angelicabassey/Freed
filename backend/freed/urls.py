from django.views.generic import TemplateView
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from . import views

urlpatterns = [
    path('docs/', TemplateView.as_view(
        template_name='docs.html',
        extra_context={'schema_url':'api_schema'}
        ), name='swagger-ui'),
    path('moralis_auth', views.moralis_auth, name='moralis_auth'),
    path('my_profile', views.my_profile, name='my_profile'),
    path('request_message', views.SendChallengeView.as_view(), name='request_message'),
    path('verify_message', views.VerifyMessageView.as_view(), name='verify_message'),
]
