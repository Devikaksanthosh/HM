from django.urls import path
from .views import predict_mental_health

urlpatterns = [
    path("predict/", predict_mental_health, name="predict_mental_health"),
]
