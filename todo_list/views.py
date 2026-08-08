from django.views import generic
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.urls import reverse_lazy

from todo_list.models import Task, Tag
from todo_list.forms import TaskForm


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


class TaskCreateView(CancelUrlMixin, generic.CreateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy("todo_list:task-list")


class TaskUpdateView(CancelUrlMixin, generic.UpdateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy("todo_list:task-list")


class TaskDeleteView(CancelUrlMixin, generic.DeleteView):
    model = Task
    success_url = reverse_lazy("todo_list:task-list")


class TagListView(generic.ListView):
    model = Tag


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


@require_http_methods(["POST"])
def complete_undo_status_from_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.is_completed = not task.is_completed
    task.save()
    return redirect("todo_list:task-list")
