from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Task


class TaskApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="alex", password="test-password")
        self.other_user = get_user_model().objects.create_user(username="sam", password="test-password")
        self.client.force_authenticate(self.user)

    def test_view_all_tasks(self):
        Task.objects.create(title="First task", owner=self.user)
        Task.objects.create(title="Second task", owner=self.user)

        response = self.client.get(reverse("task-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_anonymous_users_cannot_access_tasks(self):
        self.client.force_authenticate(user=None)

        response = self.client.get(reverse("task-list"))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_task_is_stored_in_database(self):
        response = self.client.post(
            reverse("task-list"),
            {
                "title": "Learn Python",
                "description": "Practice Python functions",
                "priority": "high",
                "status": "todo",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Task.objects.filter(title="Learn Python", priority="high", owner=self.user).exists())

    def test_edit_task(self):
        task = Task.objects.create(title="Old title", owner=self.user)

        response = self.client.patch(
            reverse("task-detail", args=[task.id]),
            {"title": "Updated title", "description": "New details"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.title, "Updated title")
        self.assertEqual(task.description, "New details")

    def test_delete_task(self):
        task = Task.objects.create(title="Remove me", owner=self.user)

        response = self.client.delete(reverse("task-detail", args=[task.id]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=task.id).exists())

    def test_mark_task_completed_and_pending(self):
        task = Task.objects.create(title="Finish feature", owner=self.user)

        completed_response = self.client.patch(
            reverse("task-detail", args=[task.id]),
            {"status": Task.Status.DONE},
            format="json",
        )
        task.refresh_from_db()
        self.assertEqual(completed_response.status_code, status.HTTP_200_OK)
        self.assertEqual(task.status, Task.Status.DONE)

        pending_response = self.client.patch(
            reverse("task-detail", args=[task.id]),
            {"status": Task.Status.TODO},
            format="json",
        )
        task.refresh_from_db()
        self.assertEqual(pending_response.status_code, status.HTTP_200_OK)
        self.assertEqual(task.status, Task.Status.TODO)

    def test_create_task_requires_title(self):
        response = self.client.post(reverse("task-list"), {"title": "   "}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_tasks_by_status(self):
        Task.objects.create(title="Ship release", status=Task.Status.DONE, owner=self.user)
        Task.objects.create(title="Write notes", status=Task.Status.TODO, owner=self.user)
        response = self.client.get(reverse("task-list"), {"status": "done"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Ship release")

    def test_users_only_see_their_own_tasks(self):
        Task.objects.create(title="Alex task", owner=self.user)
        Task.objects.create(title="Sam task", owner=self.other_user)

        response = self.client.get(reverse("task-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([task["title"] for task in response.data["results"]], ["Alex task"])