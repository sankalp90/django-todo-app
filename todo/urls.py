from django.urls import path
from . import views

urlpatterns =[
    path('',views.todo_list,name='todo_list'),
    path('toggle/<int:task_id>/', views.toggle_complete, name='toggle_complete'),
    path('dashboard/',views.dashboard,name = 'dashboard'),
]