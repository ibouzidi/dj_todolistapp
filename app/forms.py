from .models import Task
from django import forms
from datetime import datetime
from django.utils import timezone


class AddTask(forms.ModelForm):
    class Meta:
        model = Task
        fields = {'title', 'description', 'complete', 'due_date', 'priority'}
        widgets = {
            'due_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local', 'min': timezone.now()}),
            'priority': forms.Select(attrs={'class': 'form-all'})
        }

