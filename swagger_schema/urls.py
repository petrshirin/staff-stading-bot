from rest_framework_swagger.views import get_swagger_view
from django.urls import path, include

schema_view = get_swagger_view(title='Staff API')

urlpatterns = [
    path('', schema_view)
]