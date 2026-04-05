from django.shortcuts import render, redirect, get_object_or_404
from .models import Todo
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q


@login_required
def todo_list(request):
    todos = Todo.objects.filter(user=request.user)
    todos = filter_todos(request, todos)

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
                    user=request.user,
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
            due_date = request.POST.get("due_date")

            if due_date:
                due_date = parse_datetime(due_date)
            else:
                due_date = timezone.now()  

            todo.due_date = due_date

            todo.priority = request.POST.get("priority")
            todo.completed = True if request.POST.get("completed") == "on" else False

            todo.save()
            return redirect("todo_list")

        if "delete_task" in request.POST:
            task_id = request.POST.get("task_id")
            todo = get_object_or_404(Todo, id=task_id, user = request.user)
            todo.delete()
            return redirect("todo_list")

        if "clear_all" in request.POST:
            Todo.objects.all().delete()
            return redirect("todo_list")

    return render(request, "todo/list.html", {
        "todos": todos,
        "task_count": len(todos)
    })

def filter_todos(request,queryset):
    search = request.GET.get("search")
    priority = request.GET.get("priority")
    status = request.GET.get("status")
    sort = request.GET.get("sort")
    overdue = request.GET.get("overdue")

    if  search:
        queryset = queryset.filter(
            Q(title__icontains = search) |
            Q(description__icontains = search)
        )
    
    if priority :
        queryset = queryset.filter(priority=priority)

    if status:
        if status == "completed":
            queryset = queryset.filter(completed = True)
        elif status == "pending":
            queryset = queryset.filter(completed = False)
    
    if overdue == "true":
        queryset = queryset.filter(
            due_date__lt=timezone.now(),
            completed=False
        )
    
    if sort == "due_date":
        queryset = queryset.order_by("due_date")
    
    elif sort == "-due_date":
        queryset = queryset.order_by("-due_date")
    else:
        queryset = queryset.order_by("-id")

    return queryset