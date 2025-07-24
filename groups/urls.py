from django.urls import path

from .apis import (GroupsAPI, GroupAPI, CreateAPI, RequestsAPI, AdminStaffsAPI,
                   InvitesAPI, DeleteInviteAPI,)

urlpatterns = [
    path("<int:id>/", GroupsAPI.as_view()),
    path("group/<int:id>/", GroupAPI.as_view()),
    path("create/", CreateAPI.as_view()),
    path("joinrequest/<int:group_id>/<str:type>/", RequestsAPI.as_view()),
    path("admin/<int:group_id>/<str:type>/", AdminStaffsAPI.as_view()),
    path("invite/", InvitesAPI.as_view()),
    path("invite/<int:id>/", DeleteInviteAPI.as_view()),
]
