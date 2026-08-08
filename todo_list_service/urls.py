from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("todo_list.urls", namespace="todo_list")),
    path("__debug__/", include("debug_toolbar.urls")),
]
