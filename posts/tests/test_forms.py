from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='TestUser')
        cls.post = Post.objects.create(author=cls.author,
                                       text='Тестовый пост')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_create_post_in_form(self):
        """Форма создаёт пост в базе."""
        post_count = Post.objects.count()
        form_data = {'text': 'Тестовый пост из формы'}
        self.authorized_client.post(reverse('posts:new_post'), data=form_data)
        self.assertEqual(Post.objects.count(), post_count + 1)

    def test_edit_post_in_form(self):
        """проверка редактирования поста."""
        form_data = {'text': 'Новый текст'}
        self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'username': self.author.username,
                            'post_id': self.post.id}),
            data=form_data
        )
        response = self.authorized_client.get(
            f'/{self.author.username}/{self.post.id}/',
        )
        self.assertEqual(response.context['post'].text, 'Новый текст')