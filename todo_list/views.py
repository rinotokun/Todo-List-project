from django.views import generic
from django.urls import reverse_lazy

from todo_list.models import Task, Tag


class CancelUrlMixin:

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = self.request.GET.get(
            "next",
            self.success_url
        )
        return context


class TaskListView(generic.ListView):
    model = Task
    queryset = Task.objects.prefetch_related("tags")
    paginate_by = 5


class TaskCreateView(CancelUrlMixin, generic.CreateView):
    model = Task
    fields = "__all__"
    success_url = reverse_lazy("todo_list:task-list")


class TaskUpdateView(CancelUrlMixin, generic.UpdateView):
    model = Task
    fields = "__all__"
    success_url = reverse_lazy("todo_list:task-list")


class TaskDeleteView(CancelUrlMixin, generic.DeleteView):
    model = Task
    success_url = reverse_lazy("todo_list:task-list")


class TagListView(generic.ListView):
    model = Tag
    paginate_by = 5


class TagCreateView(CancelUrlMixin, generic.CreateView):
    model = Tag
    fields = "__all__"
    success_url = reverse_lazy("todo_list:tag-list")


class TagUpdateView(CancelUrlMixin, generic.UpdateView):
    model = Tag
    fields = "__all__"
    success_url = reverse_lazy("todo_list:tag-list")


class TagDeleteView(CancelUrlMixin, generic.DeleteView):
    model = Tag
    success_url = reverse_lazy("todo_list:tag-list")
