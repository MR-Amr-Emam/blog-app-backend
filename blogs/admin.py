from django.contrib import admin
from .models import Blog, Section, Comment, Category

admin.site.register(Blog)
admin.site.register(Section)
admin.site.register(Comment)
admin.site.register(Category)