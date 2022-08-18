# posts/tests/test_views.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import datetime
from posts.models import Post, Group, User
from posts.forms import PostForm
from django.core.paginator import Page

User = get_user_model()
POSTS_PER_PAGE = 10


class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            description='Описание',
            title='Имя',
            slug='test-slug'
        )

        cls.author_user = User.objects.create_user(username='hasNoName')

        cls.posts = [
            Post.objects.create(
                text='Тестовый текст ' + str(i),
                pub_date='Тестовая дата ' + str(i),
                author=PostsViewsTests.author_user,
                group=PostsViewsTests.group
            )
            for i in range(POSTS_PER_PAGE)
        ]

        cls.post = PostsViewsTests.posts[0]
        cls.paginate_obj = PaginatorViewsTest()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsViewsTests.post.author)

    def check_form_fields_list(self, response, form_fields):
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get(value)
                self.assertIsInstance(form_field, expected)

    def check_post_after_create_with_group(self, response):
        self.assertTrue(self.post in response.context['page_obj'])

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',

            reverse('posts:group_list',
                    kwargs={'slug': PostsViewsTests.group.slug}):
                        'posts/group_list.html',

            reverse('posts:profile',
                    kwargs={'username': PostsViewsTests.post.author}):
                        'posts/profile.html',

            reverse('posts:post_detail',
                    kwargs={'post_id': PostsViewsTests.post.pk}):
                        'posts/post_detail.html',

            reverse('posts:post_create'): 'posts/create_post.html',

            reverse('posts:post_edit',
                    kwargs={'post_id': PostsViewsTests.post.pk}):
                        'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
        """Корректные данные в контексте главой страницы"""
        response = self.authorized_client.get(reverse('posts:index'))
        form_field = response.context.get('page_obj')
        self.assertIsInstance(form_field, Page)

        """
        В тестах страниц index, group_list и profile помимо проверки контекста
        вставила вызовы методов проверки на паджинатор и на отображение
        поста после создания.
        С одной стороны тесты стали проверять больше заявленного,
        с другой - не дублируется очень большое количество кода.
        Так и не смогла решить, что лучше.
        """

        PostsViewsTests.paginate_obj.page_contain_ten_records(
            response=response
        )

        self.check_post_after_create_with_group(response=response)

    def test_group_list_show_correct_context(self):
        """Корректные данные в контексте страницы повтов группы"""
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': PostsViewsTests.group.slug})
        )
        form_fields = {
            'group': Group,
            'page_obj': Page,
        }

        self.check_form_fields_list(response, form_fields)

        PostsViewsTests.paginate_obj.page_contain_ten_records(
            response=response
        )

        self.check_post_after_create_with_group(response=response)

    def test_profile_show_correct_context(self):
        """Корректные данные в контексте страницы повтов автора"""
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': PostsViewsTests.post.author})
        )
        form_fields = {
            'page_obj': Page,
            'author': User,
            'posts_amount': int,
        }

        self.check_form_fields_list(response, form_fields)

        PostsViewsTests.paginate_obj.page_contain_ten_records(
            response=response
        )

        self.check_post_after_create_with_group(response=response)

    def test_post_detail_show_correct_context(self):
        """Корректные данные в контексте страницы поста"""
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': PostsViewsTests.post.pk})
        )
        form_fields = {
            "post": Post,
            "post_title": str,
            "pub_date": datetime,
            "author": User,
            "author_posts_amount": int,
        }

        self.check_form_fields_list(response, form_fields)

    def test_post_edit_show_correct_context(self):
        """Корректные данные в контексте страницы редактирования поста"""
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': PostsViewsTests.post.pk})
        )
        form_fields = {
            "is_edit": bool,
            "form": PostForm,
        }

        self.check_form_fields_list(response, form_fields)

    def test_post_create_show_correct_context(self):
        """Корректные данные в контексте страницы создания поста"""
        response = self.authorized_client.get(
            reverse('posts:post_create')
        )
        form_field = response.context.get('form')
        self.assertIsInstance(form_field, PostForm)

    def test_created_post_not_in_other_group(self):
        """Созданный пост с группой не попал в другую группу"""
        fake_group = Group.objects.create(
            description='fake_group',
            title='fake_group',
            slug='test-fake-slug'
        )
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': fake_group.slug})
        )
        self.assertTrue(self.post not in response.context['page_obj'])


class PaginatorViewsTest(TestCase):
    def page_contain_ten_records(self, response):
        """На странице доступно заданное число постов"""
        self.assertEqual(len(response.context['page_obj']), POSTS_PER_PAGE)
