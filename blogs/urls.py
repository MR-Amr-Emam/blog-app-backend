from django.urls import path

from .apis import (BlogApi, CreateBlogApi,
    BlogsApi, HomeBlogsApi,
    AddCommentAPI, CommentsAPI,
    CommentAPI, CategorysAPI)


urlpatterns = [
    path("home/", HomeBlogsApi.as_view()),
    path("home/<int:id>/", HomeBlogsApi.as_view()),
    path("<int:id>/", BlogsApi.as_view()),
    path("<int:id>/<str:type>/", BlogsApi.as_view()),
    path("blog/<int:id>/", BlogApi.as_view()),
    path("blog/<int:id>/comment/", AddCommentAPI.as_view()),
    path("blog/<int:id>/comments/", CommentsAPI.as_view()),
    path("blog/<int:id>/<slug:mini>/", BlogApi.as_view()),
    path("blog/create/", CreateBlogApi.as_view()),
    path("comment/<int:id>/", CommentAPI.as_view()),
    path("categorys/", CategorysAPI.as_view()),
]

