from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(title='Тестовое название',
                                         slug='test-slug',
                                         description='Тестовое описание')

        cls.post = Post.objects.create(
            text='Тестовый пост длинной более 15 символов',
            author=cls.user,
            group=cls.group
        )
        cls.templates_pages_names = {
            'index.html': reverse('posts:index'),
            'group.html': reverse('posts:group_posts',
                                  kwargs={'slug': 'test-slug'}),
            'new.html': reverse('posts:new_post')
        }

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for template, reverse_name in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_context_in_template_index(self):
        """
        Шаблон index сформирован с правильным контекстом.
        При создании поста с указанием группы,
        этот пост появляется на главной странице сайта.
        """
        response = self.authorized_client.get(reverse('posts:index'))
        last_post = response.context['page'][0]
        self.assertEqual(last_post, self.post)

    def test_context_in_template_group(self):
        """
        Шаблон group сформирован с правильным контекстом.
        При создании поста с указанием группы,
        этот пост появляется на странице этой группы.
        """
        response = self.authorized_client.get \
            (reverse('posts:group_posts',
                     kwargs={'slug': 'test-slug'}))
        test_group = response.context['group']
        test_post = response.context['page'][0].__str__()
        self.assertEqual(test_group, self.group)
        self.assertEqual(test_post, self.post.__str__())

    def test_context_in_template_new_post(self):
        """Шаблон new сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:new_post'))

        form_fields = {'group': forms.fields.ChoiceField,
                       'text': forms.fields.CharField}

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_context_in_post_edit_template(self):
        """Шаблон редактирования поста сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'username': self.user.username,
                            'post_id': self.post.id}),
        )

        form_fields = {
            'text': forms.fields.CharField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_context_in_template_profile(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(f'/{self.user.username}/')
        profile = {'post_count': self.user.posts.count(),
                   'author': self.post.author}

        for value, expected in profile.items():
            with self.subTest(value=value):
                context = response.context[value]
                self.assertEqual(context, expected)

        test_page = response.context['page'][0]
        self.assertEqual(test_page, self.user.posts.all()[0])

    def test_context_in_template_post(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            f'/{self.user.username}/{self.post.id}/'
        )

        profile = {'post_count': self.user.posts.count(),
                   'author': self.post.author,
                   'post': self.post}

        for value, expected in profile.items():
            with self.subTest(value=value):
                context = response.context[value]
                self.assertEqual(context, expected)

    def test_post_not_add_another_group(self):
        """
        При создании поста с указанием группы,
        этот пост НЕ попал в группу, для которой не был предназначен.
        """
        response = self.authorized_client.get(reverse('posts:index'))
        post = response.context['page'][0]
        group = post.group
        self.assertEqual(group, self.group)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Test User')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        for count in range(13):
            cls.post = Post.objects.create(
                text=f'Тестовый пост номер {count}',
                author=cls.user)

    def test_first_page_containse_ten_records(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_containse_three_records(self):
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2'
        )
        self.assertEqual(len(response.context.get('page').object_list), 3)
