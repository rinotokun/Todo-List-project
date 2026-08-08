from datetime import datetime

from django.test import TestCase
from django.utils import timezone

from todo_list.forms import TaskForm
from todo_list.models import Tag


class TaskFormTest(TestCase):

    def setUp(self):
        self.tag = Tag.objects.create(name="home")

    def test_form_is_valid_without_a_deadline(self):
        form = TaskForm(
            data={
                "content": "Water the plants",
                "deadline": "",
                "tags": [self.tag.pk],
            }
        )

        self.assertTrue(form.is_valid())
        self.assertIsNone(form.cleaned_data["deadline"])

    def test_form_is_valid_without_tags(self):
        form = TaskForm(
            data={
                "content": "Water the plants",
                "deadline": "",
                "tags": [],
            }
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(list(form.cleaned_data["tags"]), [])

    def test_form_requires_content(self):
        form = TaskForm(
            data={
                "content": "",
                "deadline": "",
                "tags": [self.tag.pk],
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("content", form.errors)

    def test_form_understands_the_datetime_local_format(self):
        form = TaskForm(
            data={
                "content": "Send the weekly report",
                "deadline": "2026-09-22T18:30",
                "tags": [],
            }
        )

        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data["deadline"],
            timezone.make_aware(datetime(2026, 9, 22, 18, 30)),
        )

    def test_form_has_no_field_for_the_completion_status(self):
        self.assertNotIn("is_completed", TaskForm().fields)

    def test_deadline_is_rendered_as_a_native_datetime_picker(self):
        rendered_field = str(TaskForm()["deadline"])

        self.assertIn('type="datetime-local"', rendered_field)
