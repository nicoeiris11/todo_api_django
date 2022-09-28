from .models import Todo


class TodoService:
    """
    Service to encapsulate Todo business logic
    """

    def __init__(self) -> None:
        pass

    def _get_todo(self, pk: int) -> Todo:
        return Todo.objects.get(pk=pk)

    def _branch_is_complete_rec(self, todo: Todo) -> bool:
        """
        base case: if Todo not complete or Todo without childs compute status
        recursion: loop children and break iter if at least one is not complete
        """
        if not todo.is_complete:
            return False

        if len(todo.children.all()) == 0:
            return True

        is_complete = True
        for child in todo.children.all():
            sub_branch_complete = self._branch_is_complete_rec(child)
            if not sub_branch_complete:
                is_complete = False
                break

        return is_complete

    def update_parents(self, pk: int) -> None:
        """
        Searches todo in db and updates parents status in the DB
        """
        todo = self._get_todo(pk)
        parent = todo.parent

        while parent is not None:
            parent.is_complete = todo.is_complete
            parent.save()
            parent = parent.parent

    def branch_status(self, pk: int) -> tuple[str, bool]:
        """
        Navigates recursivelly through children to check if all are complete.
        Assumes empty children list as complete
        """
        todo = self._get_todo(pk)
        children_is_complete = []
        for child in todo.children.all():
            children_is_complete.append(self._branch_is_complete_rec(child))

        return todo.name, all(children_is_complete)

    def complete(self, pk: int) -> None:
        """
        Search Todo and mark it as complete.
        Also iterate over children list and mark is as complete (1st childs level only)
        """
        todo = self._get_todo(pk)
        if not todo.is_complete:
            todo.is_complete = True
            todo.save()

        for child in todo.children.all():
            if not child.is_complete:
                child.is_complete = True
                child.save()
