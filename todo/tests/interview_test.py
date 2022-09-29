import json
from datetime import datetime

import factory
from django.core import management
from django.test import TestCase
from django.urls import reverse
from faker import Factory
from rest_framework import status
from rest_framework.test import APIClient

from ..models import Todo
from .factories import TodoFactory, CompleteTodoFactory, IncompleteTodoFactory


faker = Factory.create()


class InterviewTodoListFactory:
    def build(self):
        root = IncompleteTodoFactory(name="TODO List")
        todo_a = IncompleteTodoFactory(parent=root, name="TODO A")
        todo_a1 = CompleteTodoFactory(parent=todo_a, name="TODO A1")
        todo_a2 = IncompleteTodoFactory(parent=todo_a, name="TODO A2")
        todo_a2_1 = CompleteTodoFactory(parent=todo_a2, name="TODO A2.1")
        todo_a2_2 = IncompleteTodoFactory(parent=todo_a2, name="TODO A2.2")
        todo_a2_3 = CompleteTodoFactory(parent=todo_a2, name="TODO A2.3")
        todo_a3 = IncompleteTodoFactory(parent=todo_a, name="TODO A3")
        todo_a3_1 = IncompleteTodoFactory(parent=todo_a3, name="TODO A3.1")
        todo_a3_1_1 = IncompleteTodoFactory(parent=todo_a3_1, name="TODO A3.1.1")
        todo_a3_1_2 = CompleteTodoFactory(parent=todo_a3_1, name="TODO A3.1.2")
        todo_a3_1_3 = IncompleteTodoFactory(parent=todo_a3_1, name="TODO A3.1.3")
        todo_a3_2 = CompleteTodoFactory(parent=todo_a3, name="TODO A3.2")
        todo_b = CompleteTodoFactory(parent=root, name="TODO B")
        todo_b1 = CompleteTodoFactory(parent=todo_b, name="TODO B1")
        todo_b2 = CompleteTodoFactory(parent=todo_b, name="TODO B2")
        todo_c = CompleteTodoFactory(parent=root, name="TODO C")
        todo_c1 = CompleteTodoFactory(parent=todo_c, name="TODO C1")
        todo_c2 = CompleteTodoFactory(parent=todo_c, name="TODO C2")
        todo_c2_1 = IncompleteTodoFactory(parent=todo_c2, name="TODO C2.1")
        return root


class Interview_Test(TestCase):
    def setUp(self):
        self.api_client = APIClient()
        self.todo_list = InterviewTodoListFactory().build()

    def test_update_parents(self):
        todo_root = Todo.objects.get(name="TODO List")
        todo_a = Todo.objects.get(name="TODO A")
        todo_a1 = Todo.objects.get(name="TODO A1")
        update_parents_url = reverse("update-parents-post", args=[todo_a1.id])
        assert not todo_root.is_complete and not todo_a.is_complete
        response = self.api_client.post(update_parents_url)
        assert response.status_code == status.HTTP_200_OK
        todo_a.refresh_from_db()
        todo_root.refresh_from_db()
        assert todo_root.is_complete and todo_a.is_complete

    def test_update_parents_not_found(self):
        update_parents_url = reverse("update-parents-post", args=[999])
        response = self.api_client.post(update_parents_url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_branch_status_empty_children(self):
        todo_b1 = Todo.objects.get(name="TODO B1")
        branch_status_url = reverse("branch-status-get", args=[todo_b1.id])
        response = self.api_client.get(branch_status_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == "Todo TODO B1 is complete"

    def test_branch_status_complete(self):
        todo_b = Todo.objects.get(name="TODO B")
        branch_status_url = reverse("branch-status-get", args=[todo_b.id])
        response = self.api_client.get(branch_status_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == "Todo TODO B is complete"

    def test_branch_status_incomplete(self):
        todo_c = Todo.objects.get(name="TODO C")
        branch_status_url = reverse("branch-status-get", args=[todo_c.id])
        response = self.api_client.get(branch_status_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == "Todo TODO C is incomplete"

    def test_branch_status_not_found(self):
        branch_status_url = reverse("branch-status-get", args=[999])
        response = self.api_client.get(branch_status_url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_complete(self):
        todo_a3_1 = Todo.objects.get(name="TODO A3.1")
        todo_a3_1_1 = Todo.objects.get(name="TODO A3.1.1")
        todo_a3_1_2 = Todo.objects.get(name="TODO A3.1.2")
        todo_a3_1_3 = Todo.objects.get(name="TODO A3.1.3")
        complete_url = reverse("complete-post", args=[todo_a3_1.id])
        assert not todo_a3_1.is_complete
        assert not todo_a3_1_1.is_complete
        assert todo_a3_1_2.is_complete
        assert not todo_a3_1_3.is_complete
        response = self.api_client.post(complete_url)
        assert response.status_code == status.HTTP_200_OK
        todo_a3_1.refresh_from_db()
        todo_a3_1_1.refresh_from_db()
        todo_a3_1_2.refresh_from_db()
        todo_a3_1_3.refresh_from_db()
        assert todo_a3_1.is_complete
        assert todo_a3_1_1.is_complete
        assert todo_a3_1_2.is_complete
        assert todo_a3_1_3.is_complete

    def test_complete_empty_children(self):
        todo_a3_1_3 = Todo.objects.get(name="TODO A3.1.3")
        complete_url = reverse("complete-post", args=[todo_a3_1_3.id])
        assert not todo_a3_1_3.is_complete
        response = self.api_client.post(complete_url)
        assert response.status_code == status.HTTP_200_OK
        todo_a3_1_3.refresh_from_db()
        assert todo_a3_1_3.is_complete

    def test_complete_not_found(self):
        complete_url = reverse("complete-post", args=[999])
        response = self.api_client.post(complete_url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_with_children(self):
        count_pre_delete = Todo.objects.count()
        todo_b = Todo.objects.get(name="TODO B")
        response = self.api_client.delete(
            reverse("todo-detail", kwargs={"pk": todo_b.id})
        )
        count_post_delete = Todo.objects.count()
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert count_post_delete == count_pre_delete - 3
