from django.urls import path
from .apis import Secure, GetPairTokenAPI, RefreshTokenAPI

urlpatterns = [
    path('api/token/', GetPairTokenAPI.as_view()),
    path('api/token/refresh/', RefreshTokenAPI.as_view()),
    path('secure/', Secure.as_view()),
]