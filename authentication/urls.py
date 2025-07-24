from django.urls import path
from .apis import (GetPairTokenAPI,
                   RefreshTokenAPI,
                   UserProfileAPI,
                   SearchUsers,
                   SearchUsersById,
                   UserFriendsAPI,
                   Public)

urlpatterns = [
    path('token/', GetPairTokenAPI.as_view()),
    path('token/refresh/', RefreshTokenAPI.as_view()),
    path('users-info/ids/', SearchUsersById.as_view()),
    path('users-info/<str:search_param>/', SearchUsers.as_view()),
    path('user-info/<int:id>/', UserProfileAPI.as_view()),
    path('user-friends/<int:id>/', UserFriendsAPI.as_view()),
    path('public/', Public.as_view()),
]