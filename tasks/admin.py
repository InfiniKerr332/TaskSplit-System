from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db import transaction

from .models import Membership, Project, Task, User


admin.site.site_header = 'TaskSplit administration'


@admin.register(User)
class TaskSplitUserAdmin(UserAdmin):
    add_fieldsets = (
        (None, {'classes': ['wide'], 'fields': ['username', 'email', 'password1', 'password2']}),
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'leader', 'created_at']
    search_fields = ['name', 'leader__email']
    readonly_fields = ['join_code', 'created_at']

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return [*self.readonly_fields, 'leader']
        return self.readonly_fields

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        Membership.objects.get_or_create(project=obj, user=obj.leader)


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'project', 'joined_at']
    list_filter = ['project']
    readonly_fields = ['joined_at']
    actions = None

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return [*self.readonly_fields, 'project', 'user']
        return self.readonly_fields

    def has_delete_permission(self, request, obj=None):
        if obj and obj.user_id == obj.project.leader_id:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'assigned_to', 'deadline', 'status', 'priority']
    list_filter = ['project', 'status', 'priority']
    search_fields = ['title', 'project__name', 'assigned_to__user__username']
    readonly_fields = ['created_at', 'updated_at']
