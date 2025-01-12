from django.urls import path
from . import views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import register_user, login_user, protected_view
from rest_framework_simplejwt.views import TokenRefreshView


schema_view = get_schema_view(
    openapi.Info(
        title="Your API Title",
        default_version='v1',
        description="API documentation with Swagger",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="your_email@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('reverse-complement/', views.reverse_complement_view, name='reverse_complement'),
    path('gc-content-graph/', views.gc_content_graph_view, name='gc_content_graph'),
    path('protein-translation/', views.protein_translation_view, name='protein_translation'),
    path('mutation-detection/', views.mutation_detection_view, name='mutation_detection'),
    path('validate-sequence/', views.sequence_validation_view, name='sequence_validation'),
    path('generate-report/', views.generate_report_view, name='generate_report'),  # New PDF Report Endpoint
    path('interactive-gc-content/', views.interactive_gc_content_view, name='interactive_gc_content'),  # New Interactive Graph Endpoint
      path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('protected/', protected_view, name='protected'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-doc'),
]
