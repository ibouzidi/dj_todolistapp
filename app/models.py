from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


def one_week_hence():
    return timezone.now() + timezone.timedelta(days=7)


PRIORITY_CHOICES = [
    ('low', 'low'),
    ('normal', 'normal'),
    ('medium', 'medium'),
    ('high', 'high')
]


class Task(models.Model):
    class Priority(models.IntegerChoices):
        LOW = 1, "Low"
        MEDIUM = 2, "Medium"
        HIGH = 3, "High"
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=40)
    description = models.TextField(null=True, blank=True)
    complete = models.BooleanField(default=False)
    create = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(default=one_week_hence)
    priority = models.PositiveSmallIntegerField(choices=Priority.choices,
                                                db_index=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-due_date']
