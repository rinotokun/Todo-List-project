from django import forms
from django_select2.forms import Select2MultipleWidget

from todo_list.models import Task, Tag


class TaskForm(forms.ModelForm):
    deadline = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            format="%Y-%m-%dT%H:%M",
            attrs={
                "type": "datetime-local",
                "class": "form-control"
            }
        ),
    )
    tags = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Tag.objects.all(),
        widget=Select2MultipleWidget(
            attrs={
                "data-theme": "bootstrap-5"
            }
        ),
    )

    class Meta:
        model = Task
        fields = ["content", "deadline", "tags"]
