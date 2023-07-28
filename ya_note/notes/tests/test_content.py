from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestHomePage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=cls.author
        )
        cls.auth_client = Client()

    def test_notes_list_for_different_users(self):
        users_statuses = (
            (self.author, True),
            (self.reader, False),
        )
        for user, status in users_statuses:
            with self.subTest():
                self.auth_client.force_login(user)
                response = self.auth_client.get(reverse('notes:list'))
                object_list = response.context['object_list']
                self.assertIs(self.note in object_list, status)

    def test_pages_contains_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', {'slug': self.note.slug}),
        )
        for name, kwargs in urls:
            with self.subTest():
                self.auth_client.force_login(self.author)
                response = self.auth_client.get(reverse(name, kwargs=kwargs))
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
