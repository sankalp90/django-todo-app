from django.shortcuts import render, redirect, get_object_or_404
from .models import Todo, Category
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.shortcuts import render
from datetime import timedelta 
from django.db.models.functions import TruncDate 


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
            category_id = request.POST.get("category")

            # Fix due_date
            due_date = parse_datetime(due_date) if due_date else None

            # Fix category (ForeignKey)
            category = None
            if category_id:
                category = Category.objects.filter(id=category_id, user=request.user).first()

            if title:
                Todo.objects.create(
                    user=request.user,
                    title=title,
                    description=description,
                    due_date=due_date,
                    priority=priority if priority else 'M',
                    category=category,
                )
            return redirect("todo_list")
        
        if "add_category" in request.POST:
            name = request.POST.get("new_category")

            if name:
                Category.objects.create(
                    name=name,
                    user=request.user
                )

            return redirect("todo_list")

        if "edit_task" in request.POST:
            task_id = request.POST.get("task_id")
            todo = get_object_or_404(Todo, id=task_id, user=request.user)

            todo.title = request.POST.get("title")
            todo.description = request.POST.get("description")

            # Fix category update
            category_id = request.POST.get("category")
            if category_id:
                todo.category = Category.objects.filter(id=category_id, user=request.user).first()
            else:
                todo.category = None

            # Fix due_date
            due_date = request.POST.get("due_date")
            todo.due_date = parse_datetime(due_date) if due_date else None

            todo.priority = request.POST.get("priority")
            #todo.completed = True if request.POST.get("completed") == "on" 

            todo.save()
            return redirect("todo_list")

        if "delete_task" in request.POST:
            task_id = request.POST.get("task_id")
            todo = get_object_or_404(Todo, id=task_id, user=request.user)
            todo.delete()
            return redirect("todo_list")

        if "clear_all" in request.POST:
            # Fix: delete only current user's tasks
            Todo.objects.filter(user=request.user).delete()
            return redirect("todo_list")

    return render(request, "todo/list.html", {
        "todos": todos,
        "task_count": todos.count(),
        "categories": Category.objects.filter(user=request.user)
    })

@login_required
def toggle_complete(request, task_id):
    todo = get_object_or_404(Todo, id=task_id, user=request.user)
    todo.completed = not todo.completed
    todo.save()
    return redirect("todo_list")  


def filter_todos(request, queryset):
    search = request.GET.get("search")
    priority = request.GET.get("priority")
    status = request.GET.get("status")
    sort = request.GET.get("sort")
    overdue = request.GET.get("overdue")
    category = request.GET.get("category")

    if search:
        queryset = queryset.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )

    if priority:
        queryset = queryset.filter(priority=priority)

    if category:
        queryset = queryset.filter(category_id=category)

    if status:
        if status == "completed":
            queryset = queryset.filter(completed=True)
        elif status == "pending":
            queryset = queryset.filter(completed=False)

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

@login_required
def dashboard(request):
    user = request.user
    todos = Todo.objects.filter(user=user)

    total = todos.count()
    completed = todos.filter(completed=True).count()
    pending = todos.filter(completed=False).count()

    last_7_days = timezone.now() - timedelta(days=7)

    now = timezone.now()
    
    overdue = todos.filter(
        completed=False,
        due_date__lt=timezone.now()
    ).count()

    # Completion rate
    completion_rate = (completed / total * 100) if total > 0 else 0

    #  Tasks Due Today
    due_today = todos.filter(
        due_date__date=now.date(),
        completed=False
    ).count()

    #  Tasks Due This Week
    next_7_days = now + timedelta(days=7)

    due_this_week = todos.filter(
        due_date__range=(now, next_7_days),
        completed=False
    ).count()

    #  High Priority Pending
    high_priority_pending = todos.filter(
        priority='H',
        completed=False
    ).count()

    #  Weekly Comparison
    this_week = todos.filter(
        created_at__gte=now - timedelta(days=7)
    ).count()

    last_week = todos.filter(
        created_at__gte=now - timedelta(days=14),
        created_at__lt=now - timedelta(days=7)
    ).count()

    #  Top Category
    top_category = (
        todos.values('category__name')
        .annotate(count=Count('id'))
        .order_by('-count')
        .first()
    )

    tasks_over_time = (
        todos.annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )

    # Tasks completed today
    today_completed = todos.filter(
        completed=True,
        #created_at__date=timezone.now().date()
    ).count()

    # Upcoming tasks
    upcoming = todos.filter(
        completed=False,
        due_date__gte=timezone.now()
    ).order_by('due_date')[:5]

    # Category chart
    category_data = list(
        todos.values('category__name')
        .annotate(count=Count('id'))
    )

    # Priority chart
    priority_data = list(
        todos.values('priority')
        .annotate(count=Count('id'))
    )

    context = {
        'total': total,
        'completed': completed,
        'pending': pending,
        'overdue': overdue,
        'completion_rate': round(completion_rate, 2),
        'today_completed': today_completed,
        'due_today': due_today,
        'due_this_week': due_this_week,
        'high_priority_pending': high_priority_pending,
        'this_week': this_week,
        'last_week': last_week,
        'top_category': top_category,
        'upcoming': upcoming,
        'category_data': category_data,
        'priority_data': priority_data,
        'tasks_over_time': list(tasks_over_time),
    }

    return render(request, 'dashboard.html', context)