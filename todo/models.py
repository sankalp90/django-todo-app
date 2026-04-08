from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Todo(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    PRIORITY_CHOICES = [
        ('L', 'Low'),
        ('M', 'Medium'),
        ('H', 'High'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)

    priority = models.CharField(
        max_length=1,
        choices=PRIORITY_CHOICES,
        default='M',
    )

    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title