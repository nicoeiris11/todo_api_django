from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from .models import Todo
from .serializers import TodoSerializer


class TodoOperations(APIView):
    """
    Generic api view for todo operations
    """

    def get_object(self, pk):
        try:
            return Todo.objects.get(pk=pk)
        except Todo.DoesNotExist:
            raise Http404


class UpdateParentsStatus(TodoOperations):
    """
    Update parent status to be the same as the received todo
    """

    def post(self, request, pk):
        todo = self.get_object(pk)
        serializer = TodoSerializer(todo)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BranchStatus(TodoOperations):
    """
    Calculate the status of a branch (Complete or incomplete) given a todo. For
    a branch to be complete, all the children todo should be complete
    """

    def get(self, request, pk):
        todo = self.get_object(pk)
        serializer = TodoSerializer(todo)
        return Response(serializer.data, status=status.HTTP_200_OK)


class Complete(TodoOperations):
    """
    Find a todo and mark it as complete, as a result all its childs(direct descendants) should be marked as completed.
    """

    def post(self, request, pk):
        todo = self.get_object(pk)
        serializer = TodoSerializer(todo)
        return Response(serializer.data, status=status.HTTP_200_OK)
