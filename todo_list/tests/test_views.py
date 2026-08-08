from django.test import TestCase
from django.urls import reverse

from todo_list.models import Tag, Task

TASK_LIST_URL = reverse("todo_list:task-list")
TASK_CREATE_URL = reverse("todo_list:task-create")
TAG_LIST_URL = reverse("todo_list:tag-list")
TAG_CREATE_URL = reverse("todo_list:tag-create")


class TaskListViewTest(TestCase):

    def setUp(self):
        self.tag = Tag.objects.create(name="home")
        self.active_task = Task.objects.create(content="Water the plants")
        self.completed_task = Task.objects.create(
            content="Clean the windows",
            is_completed=True,
        )
        self.active_task.tags.add(self.tag)

    def test_task_list_is_available(self):
        response = self.client.get(TASK_LIST_URL)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "todo_list/task_list.html")

    def test_active_tasks_are_shown_before_completed_ones(self):
        response = self.client.get(TASK_LIST_URL)

        self.assertEqual(
            list(response.context["task_list"]),
            [self.active_task, self.completed_task],
        )

    def test_task_list_shows_every_field_of_a_task(self):
        response = self.client.get(TASK_LIST_URL)

        self.assertContains(response, "Water the plants")
        self.assertContains(response, "Clean the windows")
        self.assertContains(response, "Not done")
        self.assertContains(response, "Done")
        self.assertContains(response, "home")


class TaskCreateViewTest(TestCase):

    def setUp(self):
        self.tag = Tag.objects.create(name="work")

    def test_create_page_is_available(self):
        response = self.client.get(TASK_CREATE_URL)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "todo_list/task_form.html")

    def test_post_creates_a_task_and_redirects_to_the_list(self):
        response = self.client.post(
            TASK_CREATE_URL,
            {
                "content": "Send the weekly report",
                "deadline": "2026-09-22T18:30",
                "tags": [self.tag.pk],
            },
        )

        self.assertRedirects(response, TASK_LIST_URL)
        task = Task.objects.get(content="Send the weekly report")
        self.assertEqual(list(task.tags.all()), [self.tag])
        self.assertFalse(task.is_completed)

    def test_cancel_url_leads_to_the_task_list_by_default(self):
        response = self.client.get(TASK_CREATE_URL)

        self.assertEqual(response.context["cancel_url"], TASK_LIST_URL)

    def test_cancel_url_respects_the_next_parameter(self):
        response = self.client.get(f"{TASK_CREATE_URL}?next={TAG_LIST_URL}")

        self.assertEqual(response.context["cancel_url"], TAG_LIST_URL)


class TaskUpdateViewTest(TestCase):

    def setUp(self):
        self.task = Task.objects.create(content="Old content")
        self.url = reverse("todo_list:task-update", args=[self.task.pk])

    def test_update_page_is_available(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "todo_list/task_form.html")

    def test_post_updates_the_task(self):
        response = self.client.post(
            self.url,
            {"content": "New content", "deadline": "", "tags": []},
        )

        self.assertRedirects(response, TASK_LIST_URL)
        self.task.refresh_from_db()
        self.assertEqual(self.task.content, "New content")


class TaskDeleteViewTest(TestCase):

    def setUp(self):
        self.task = Task.objects.create(content="Task to delete")
        self.url = reverse("todo_list:task-delete", args=[self.task.pk])

    def test_delete_page_is_available(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "todo_list/task_confirm_delete.html",
        )

    def test_post_deletes_the_task(self):
        response = self.client.post(self.url)

        self.assertRedirects(response, TASK_LIST_URL)
        self.assertFalse(Task.objects.filter(pk=self.task.pk).exists())


class StatusTaskViewTest(TestCase):

    def setUp(self):
        self.active_task = Task.objects.create(content="Water the plants")
        self.completed_task = Task.objects.create(
            content="Clean the windows",
            is_completed=True,
        )

    @staticmethod
    def toggle_url(task):
        return reverse("todo_list:task-toggle-status", args=[task.pk])

    def test_post_completes_an_active_task(self):
        response = self.client.post(self.toggle_url(self.active_task))

        self.assertRedirects(response, TASK_LIST_URL)
        self.active_task.refresh_from_db()
        self.assertTrue(self.active_task.is_completed)

    def test_post_reopens_a_completed_task(self):
        response = self.client.post(self.toggle_url(self.completed_task))

        self.assertRedirects(response, TASK_LIST_URL)
        self.completed_task.refresh_from_db()
        self.assertFalse(self.completed_task.is_completed)

    def test_get_is_not_allowed_and_keeps_the_status(self):
        response = self.client.get(self.toggle_url(self.active_task))

        self.assertEqual(response.status_code, 405)
        self.active_task.refresh_from_db()
        self.assertFalse(self.active_task.is_completed)

    def test_post_for_an_unknown_task_returns_404(self):
        url = reverse("todo_list:task-toggle-status", args=[9999])

        self.assertEqual(self.client.post(url).status_code, 404)


class TagListViewTest(TestCase):

    def setUp(self):
        Tag.objects.create(name="home")
        Tag.objects.create(name="work")

    def test_tag_list_is_available(self):
        response = self.client.get(TAG_LIST_URL)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "todo_list/tag_list.html")

    def test_tag_list_shows_the_names_of_all_tags(self):
        response = self.client.get(TAG_LIST_URL)

        self.assertEqual(
            [tag.name for tag in response.context["tag_list"]],
            ["home", "work"],
        )
        self.assertContains(response, "home")
        self.assertContains(response, "work")


class TagCreateViewTest(TestCase):

    def test_create_page_is_available(self):
        response = self.client.get(TAG_CREATE_URL)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "todo_list/tag_form.html")

    def test_post_creates_a_tag_and_redirects_to_the_list(self):
        response = self.client.post(TAG_CREATE_URL, {"name": "shop"})

        self.assertRedirects(response, TAG_LIST_URL)
        self.assertTrue(Tag.objects.filter(name="shop").exists())

    def test_cancel_url_leads_to_the_tag_list_by_default(self):
        response = self.client.get(TAG_CREATE_URL)

        self.assertEqual(response.context["cancel_url"], TAG_LIST_URL)


class TagUpdateViewTest(TestCase):

    def setUp(self):
        self.tag = Tag.objects.create(name="hom")
        self.url = reverse("todo_list:tag-update", args=[self.tag.pk])

    def test_update_page_is_available(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "todo_list/tag_form.html")

    def test_post_updates_the_tag(self):
        response = self.client.post(self.url, {"name": "home"})

        self.assertRedirects(response, TAG_LIST_URL)
        self.tag.refresh_from_db()
        self.assertEqual(self.tag.name, "home")


class TagDeleteViewTest(TestCase):

    def setUp(self):
        self.tag = Tag.objects.create(name="obsolete")
        self.url = reverse("todo_list:tag-delete", args=[self.tag.pk])

    def test_delete_page_is_available(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "todo_list/tag_confirm_delete.html",
        )

    def test_post_deletes_the_tag(self):
        response = self.client.post(self.url)

        self.assertRedirects(response, TAG_LIST_URL)
        self.assertFalse(Tag.objects.filter(pk=self.tag.pk).exists())


class SidebarTest(TestCase):

    def test_sidebar_links_are_present_on_every_page(self):
        for url in (TASK_LIST_URL, TAG_LIST_URL, TASK_CREATE_URL):
            with self.subTest(url=url):
                response = self.client.get(url)

                self.assertContains(response, f'href="{TASK_LIST_URL}"')
                self.assertContains(response, f'href="{TAG_LIST_URL}"')
