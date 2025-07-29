from django.urls import path
from .apis import (GetPairTokenAPI,
                   RefreshTokenAPI,
                   UserProfileAPI,
                   SearchAPI,
                   SearchUsersById,
                   UserFriendsAPI,
                   CreateUserAPI)

urlpatterns = [
    path('token/', GetPairTokenAPI.as_view()),
    path('token/refresh/', RefreshTokenAPI.as_view()),
    path('users-info/ids/', SearchUsersById.as_view()),
    path('user-info/<int:id>/', UserProfileAPI.as_view()),
    path('user-friends/<int:id>/', UserFriendsAPI.as_view()),
    path('create/', CreateUserAPI.as_view()),
    path('search/<str:type>/<str:search_param>/', SearchAPI.as_view()),
]