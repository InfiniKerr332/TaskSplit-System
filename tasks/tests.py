import uuid
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Membership, Project, Task, User


class WeekOneTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.leader = User.objects.create_user(
            username='leader', email='leader@example.com', password='Teamwork-42-test'
        )
        cls.member = User.objects.create_user(
            username='member', email='member@example.com', password='Teamwork-42-test'
        )
        cls.outsider = User.objects.create_user(
            username='outsider', email='outsider@example.com', password='Teamwork-42-test'
        )
        cls.project = Project.objects.create(name='Thesis team', leader=cls.leader)
        cls.leader_membership = Membership.objects.create(project=cls.project, user=cls.leader)
        Membership.objects.create(project=cls.project, user=cls.member)
        cls.task = Task.objects.create(
            project=cls.project,
            title='Prepare the project proposal',
            assigned_to=cls.leader_membership,
            deadline=timezone.now() + timedelta(days=7),
        )

    def test_home_is_public(self):
        response = self.client.get(reverse('tasks:home'))
        self.assertContains(response, 'TaskSplit')
        self.assertNotContains(response, '<script')

    def test_group_pages_require_login(self):
        for name in ['group_list', 'create_group', 'join_group']:
            with self.subTest(name=name):
                self.assertEqual(self.client.get(reverse(f'tasks:{name}')).status_code, 302)
        response = self.client.get(reverse('tasks:group_detail', args=[self.project.pk]))
        self.assertEqual(response.status_code, 302)

    def test_registration_hashes_password_and_logs_user_in(self):
        response = self.client.post(reverse('tasks:register'), {
            'username': 'newmember', 'email': 'NewMember@Example.com',
            'password1': 'Project-Team-2026!', 'password2': 'Project-Team-2026!',
        })
        self.assertRedirects(response, reverse('tasks:group_list'))
        user = User.objects.get(email='newmember@example.com')
        self.assertTrue(user.check_password('Project-Team-2026!'))
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_duplicate_email_is_rejected_case_insensitively(self):
        response = self.client.post(reverse('tasks:register'), {
            'username': 'anotherleader', 'email': 'LEADER@example.com',
            'password1': 'Project-Team-2026!', 'password2': 'Project-Team-2026!',
        })
        self.assertContains(response, 'An account already uses this email address.')
        self.assertFalse(User.objects.filter(username='anotherleader').exists())

    def test_email_login_accepts_uppercase_and_rejects_bad_password(self):
        response = self.client.post(reverse('login'), {
            'username': 'LEADER@EXAMPLE.COM', 'password': 'wrong',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)
        response = self.client.post(reverse('login'), {
            'username': 'LEADER@EXAMPLE.COM', 'password': 'Teamwork-42-test',
        })
        self.assertRedirects(response, reverse('tasks:group_list'))

    def test_invalid_registration_and_group_creation_do_not_save(self):
        self.client.post(reverse('tasks:register'), {
            'username': 'weakpassword', 'email': 'weak@example.com',
            'password1': '123', 'password2': '123',
        })
        self.assertFalse(User.objects.filter(username='weakpassword').exists())
        self.client.force_login(self.member)
        response = self.client.post(reverse('tasks:create_group'), {'name': '   '})
        self.assertContains(response, 'This field is required.')
        self.assertEqual(Project.objects.count(), 1)

    def test_creator_becomes_leader_and_member(self):
        self.client.force_login(self.member)
        self.client.post(reverse('tasks:create_group'), {
            'name': 'Software project', 'description': 'Week 1', 'leader': self.outsider.pk,
        })
        project = Project.objects.get(name='Software project')
        self.assertEqual(project.leader, self.member)
        self.assertTrue(project.memberships.filter(user=self.member).exists())
        self.assertNotEqual(project.join_code, self.project.join_code)

    def test_joining_twice_keeps_one_membership(self):
        self.client.force_login(self.outsider)
        for _ in range(2):
            response = self.client.post(reverse('tasks:join_group'), {'code': str(self.project.join_code)})
            self.assertRedirects(response, reverse('tasks:group_detail', args=[self.project.pk]))
        self.assertEqual(Membership.objects.filter(project=self.project, user=self.outsider).count(), 1)

    def test_invalid_and_unknown_group_codes_show_errors(self):
        self.client.force_login(self.outsider)
        for code in ['invalid', str(uuid.uuid4())]:
            with self.subTest(code=code):
                response = self.client.post(reverse('tasks:join_group'), {'code': code})
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context['form'].errors)
        self.assertFalse(Membership.objects.filter(user=self.outsider).exists())

    def test_group_and_tasks_are_hidden_from_nonmembers(self):
        self.client.force_login(self.outsider)
        response = self.client.get(reverse('tasks:group_list'))
        self.assertNotContains(response, self.project.name)
        response = self.client.get(reverse('tasks:group_detail', args=[self.project.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertNotContains(response, self.task.title, status_code=404)

    def test_member_can_view_tasks_and_unassigned_tasks(self):
        Task.objects.create(project=self.project, title='Unassigned task', deadline=timezone.now())
        self.client.force_login(self.member)
        response = self.client.get(reverse('tasks:group_detail', args=[self.project.pk]))
        self.assertContains(response, self.task.title)
        self.assertContains(response, 'Unassigned')
        self.assertContains(response, 'Pending')
        self.assertNotContains(response, 'Add a task in Django admin')

    def test_cross_group_task_assignment_is_rejected(self):
        other_group = Project.objects.create(name='Another group', leader=self.outsider)
        foreign_member = Membership.objects.create(project=other_group, user=self.outsider)
        self.task.assigned_to = foreign_member
        with self.assertRaises(ValidationError):
            self.task.full_clean()

    def test_duplicate_membership_is_rejected_in_database(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Membership.objects.create(project=self.project, user=self.leader)

    def test_html_in_user_content_is_escaped(self):
        self.project.name = '<script>alert(1)</script>'
        self.project.save()
        self.client.force_login(self.member)
        response = self.client.get(reverse('tasks:group_detail', args=[self.project.pk]))
        self.assertNotContains(response, '<script>')
        self.assertContains(response, '&lt;script&gt;')

    def test_logout_requires_post_and_clears_session(self):
        self.client.force_login(self.member)
        self.assertEqual(self.client.get(reverse('logout')).status_code, 405)
        self.assertRedirects(self.client.post(reverse('logout')), reverse('tasks:home'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_forms_require_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post(reverse('tasks:register'), {})
        self.assertEqual(response.status_code, 403)

    def test_admin_can_create_accounts_and_tasks(self):
        self.leader.is_staff = True
        self.leader.is_superuser = True
        self.leader.save()
        self.client.force_login(self.leader)
        response = self.client.post(reverse('admin:tasks_user_add'), {
            'username': 'admincreated', 'email': 'admincreated@example.com',
            'password1': 'Project-Team-2026!', 'password2': 'Project-Team-2026!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.get(username='admincreated').has_usable_password())
        task_data = {
            'project': self.project.pk, 'title': 'Admin task',
            'assigned_to': self.leader_membership.pk,
            'deadline_0': '2026-12-01', 'deadline_1': '17:00:00',
            'status': 'pending', 'priority': 'medium',
        }
        response = self.client.post(reverse('admin:tasks_task_add'), task_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Task.objects.filter(title='Admin task').exists())
