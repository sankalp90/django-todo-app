from django.shortcuts import render, redirect, get_object_or_404
from .models import Todo
from django.utils import timezone
from django.utils.dateparse import parse_datetime

def todo_list(request):
    todos = Todo.objects.all().order_by('-id')

    if request.method == "POST":

        if "add_task" in request.POST:
            title = request.POST.get("title")
            description = request.POST.get("description")
            due_date = request.POST.get("due_date")
            priority = request.POST.get("priority")

            if due_date:
                due_date = parse_datetime(due_date)
            else:
                due_date =timezone.now()


            if title:
                Todo.objects.create(
                    title=title,
                    description=description,
                    due_date=due_date if due_date else None,
                    priority=priority if priority else 'M'
                )
            return redirect("todo_list")

        if "edit_task" in request.POST:
            task_id = request.POST.get("task_id")
            todo = get_object_or_404(Todo, id=task_id)

            todo.title = request.POST.get("title")
            todo.description = request.POST.get("description")
            todo.due_date = request.POST.get("due_date") or None

            if due_date:
                due_date = parse_datetime(due_date)
            else:
                due_date =timezone.now()
                
            todo.priority = request.POST.get("priority")
            todo.completed = True if request.POST.get("completed") == "on" else False

            todo.save()
            return redirect("todo_list")

        if "delete_task" in request.POST:
            task_id = request.POST.get("task_id")
            todo = get_object_or_404(Todo, id=task_id)
            todo.delete()
            return redirect("todo_list")

        if "clear_all" in request.POST:
            Todo.objects.all().delete()
            return redirect("todo_list")

    return render(request, "todo/list.html", {
        "todos": todos,
        "task_count": todos.count()
    })