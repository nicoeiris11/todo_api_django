from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from .models import Todo
from .serializers import TodoSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


class UpdateParentsStatus(APIView):
    """
    Update parent status to be the same as the received todo
    """

    def get_object(self, pk):
        try:
            return Todo.objects.get(pk=pk)
        except Todo.DoesNotExist:
            raise Http404

    def post(self, request, pk):
        todo = self.get_object(pk)
        serializer = TodoSerializer(todo)
        return Response(serializer.data, status=status.HTTP_200_OK)
        # serializer = TodoSerializer(todo, data=request.data)
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data, status=status.HTTP_200_OK)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BranchStatus(APIView):
    """
    Calculate the status of a branch (Complete or incomplete) given a todo. For
    a branch to be complete, all the children todo should be complete
    """

    def get_object(self, pk):
        try:
            return Todo.objects.get(pk=pk)
        except Todo.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        todo = self.get_object(pk)
        serializer = TodoSerializer(todo)
        return Response(serializer.data, status=status.HTTP_200_OK)


class Complete(APIView):
    """
    Find a todo and mark it as complete, as a result all its childs(direct descendants) should be marked as completed.
    """

    def get_object(self, pk):
        try:
            return Todo.objects.get(pk=pk)
        except Todo.DoesNotExist:
            raise Http404

    def post(self, request, pk):
        todo = self.get_object(pk)
        serializer = TodoSerializer(todo)
        return Response(serializer.data, status=status.HTTP_200_OK)
