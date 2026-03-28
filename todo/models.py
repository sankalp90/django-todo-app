from django.db import models

class Todo(models.Model):
    PRIORITY_CHOICES = [
        ('L', 'Low'),
        ('M', 'Medium'),
        ('H', 'High'),
    ]
    title = models.CharField( max_length=200)
    description = models.TextField(blank = True)
    due_date = models.DateTimeField()
    priority = models.CharField(
    max_length=1,
    choices=PRIORITY_CHOICES,
    default='M',
    )
    completed = models.BooleanField(default=False)



def __str__(self):
    return self.title