from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import JoinGroupForm, ProjectForm, RegistrationForm
from .models import Membership, Project


def home(request):
    return render(request, 'tasks/home.html')


@require_http_methods(['GET', 'POST'])
def register(request):
    if request.user.is_authenticated:
        return redirect('tasks:group_list')
    form = RegistrationForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Your account has been created.')
        return redirect('tasks:group_list')
    return render(request, 'tasks/form.html', {'form': form, 'title': 'Create an account', 'button': 'Register'})


@login_required
def group_list(request):
    groups = Project.objects.filter(memberships__user=request.user).select_related('leader')
    return render(request, 'tasks/group_list.html', {'groups': groups})


@login_required
@require_http_methods(['GET', 'POST'])
def create_group(request):
    form = ProjectForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            project = form.save(commit=False)
            project.leader = request.user
            project.save()
            Membership.objects.create(project=project, user=request.user)
        messages.success(request, 'Group created. Share the group code with your teammates.')
        return redirect('tasks:group_detail', pk=project.pk)
    return render(request, 'tasks/form.html', {'form': form, 'title': 'Create a group', 'button': 'Create group'})


@login_required
@require_http_methods(['GET', 'POST'])
def join_group(request):
    form = JoinGroupForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        project = Project.objects.filter(join_code=form.cleaned_data['code']).first()
        if project is None:
            form.add_error('code', 'No group matches this code. Ask your leader for the group code.')
        else:
            _, created = Membership.objects.get_or_create(project=project, user=request.user)
            messages.success(request, 'You joined the group.' if created else 'You are already a member of this group.')
            return redirect('tasks:group_detail', pk=project.pk)
    return render(request, 'tasks/form.html', {'form': form, 'title': 'Join a group', 'button': 'Join group'})


@login_required
def group_detail(request, pk):
    project = get_object_or_404(
        Project.objects.filter(memberships__user=request.user).select_related('leader'), pk=pk
    )
    members = project.memberships.select_related('user')
    tasks = project.tasks.select_related('assigned_to__user')
    return render(request, 'tasks/group_detail.html', {'project': project, 'members': members, 'tasks': tasks})
