from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, \
    FormView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import Task
from .forms import AddTask
from datetime import datetime, timedelta
from django.contrib import messages
from django.db.models import Case, When, Value


class CustomLoginView(LoginView):
    template_name = 'app/auth/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('tasks')


class RegisterPage(FormView):
    template_name = 'app/auth/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(self, *args, **kwargs)


class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        new_priority = Case(
            When(priority=Task.Priority.HIGH, then=Value(1)),
            When(priority=Task.Priority.MEDIUM, then=Value(2)),
            When(priority=Task.Priority.LOW, then=Value(3)),
        )
        context['tasks'] = context['tasks'].filter(
            user=self.request.user).annotate(
            new_priority=new_priority).order_by('complete', 'new_priority')
        context['count'] = context['tasks'].filter(complete=False).count()
        context['due_date'] = context['tasks'].values_list('due_date', flat=True)
        tasks = context['tasks'].all()
        # date_format = '%Y-%m-%d %H:%M:%S.%f'
        date_format = '%Y-%m-%d %H:%M:%S'
        date_now_str = datetime.now().strftime(date_format)
        for i in tasks:
            due_date = i.due_date.strftime(date_format)
            a = datetime.strptime(str(due_date), date_format)
            b = datetime.strptime(date_now_str, date_format)
            if a < b:
                i.complete = True
                i.save()

        search_input = self.request.GET.get('search') or ''
        if search_input:
            context['tasks'] = context['tasks'].filter(
                title__icontains=search_input)

        context['search_input'] = search_input
        return context


class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'


class TaskCreate(LoginRequiredMixin, CreateView):
    model = Task
    form_class = AddTask
    success_url = reverse_lazy('tasks')

    def form_valid(self, form_class):
        form_class.instance.user = self.request.user
        messages.success(self.request,
                         f'{form_class.instance} created successfully')
        return super(TaskCreate, self).form_valid(form_class)


class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = AddTask
    success_url = reverse_lazy('tasks')

    def form_valid(self, form_class):
        form_class.instance.user = self.request.user
        messages.success(self.request,
                         f'{form_class.instance} updated successfully')
        return super(UpdateView, self).form_valid(form_class)


class TaskDelete(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request,
                         f'{self.context_object_name} deleted successfully')
        return super(DeleteView, self).delete(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)