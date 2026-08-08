from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from todo_list.models import Tag, Task


class ModelTest(TestCase):

    def setUp(self):
        self.tag1 = Tag.objects.create(name="bugs")
        self.tag2 = Tag.objects.create(name="homework")
        self.tag3 = Tag.objects.create(name="django")
        self.task = Task.objects.create(
            content="Buy bread, milk and 2 kg of apples",
        )
        self.task.tags.add(self.tag1, self.tag2)

    def test_tag_str(self):
        self.assertEqual(
            str(self.tag1),
            f"{self.tag1.name}"
        )

    def test_task_str(self):
        self.assertEqual(
            str(self.task),
            f"{self.task.content}"
        )

    def test_have_only_assigned_tags(self):
        assined_tags = list(self.task.tags.all())

        self.assertIn(
            self.tag1,
            assined_tags
        )
        self.assertIn(
            self.tag2,
            assined_tags
        )
        self.assertNotIn(
            self.tag3,
            assined_tags
        )

    def test_default_is_completed_false(self):
        self.assertFalse(
            self.task.is_completed
        )

    def test_tags_ordering_by_name(self):
        result = Tag.objects.all()
        expected_result = Tag.objects.all().order_by("name")

        self.assertQuerySetEqual(
            result,
            expected_result
        )

    def test_tasks_ordering(self):
        old_active = Task.objects.create(content="Old active task")
        new_active = Task.objects.create(content="New active task")
        old_done = Task.objects.create(
            content="Old done task",
            is_completed=True,
        )
        new_done = Task.objects.create(
            content="New done task",
            is_completed=True,
        )

        moment = timezone.now()
        hours_ago = {
            new_active.pk: 1,
            new_done.pk: 2,
            old_done.pk: 3,
            old_active.pk: 4,
        }
        for task_id, hours in hours_ago.items():
            Task.objects.filter(pk=task_id).update(
                created_at=moment - timedelta(hours=hours)
            )

        self.assertEqual(
            list(Task.objects.all()),
            [
                self.task,
                new_active,
                old_active,
                new_done,
                old_done,
            ],
        )
