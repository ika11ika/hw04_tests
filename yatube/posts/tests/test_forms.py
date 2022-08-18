# posts/tests/test_forms.py
from django.test import TestCase, Client
from django.urls import reverse
from posts.models import Post, Group, User


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            description='Описание',
            title='Имя',
            slug='test-slug'
        )

        cls.author_user = User.objects.create_user(
            username='hasNoName',
            password='test'
        )

    def setUp(self):
        self.guest_client = Client()
        self.guest_client.force_login(PostCreateFormTests.author_user)

    def test_create_post(self):
        """Форма создания поста добавляет пост"""
        posts_count = Post.objects.count()

        form_data = {
            'text': 'Я не люблю тестирование!',
            'group': PostCreateFormTests.group.pk
        }

        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(
            response,
            reverse('posts:profile',
                    kwargs={'username': PostCreateFormTests.author_user})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Я не люблю тестирование!',
                author=PostCreateFormTests.author_user,
                group=PostCreateFormTests.group
            ).exists()
        )


class PostEditFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            description='Описание',
            title='Имя',
            slug='test-slug'
        )

        cls.author_user = User.objects.create_user(
            username='hasNoName',
            password='test'
        )

        cls.post = Post.objects.create(
            text='Тестовый текст',
            pub_date='Тестовая дата',
            author=PostEditFormTests.author_user,
            group=PostEditFormTests.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.guest_client.force_login(PostEditFormTests.author_user)

    def test_edit_post(self):
        """Форма редактирования поста изменяет пост"""
        posts_count = Post.objects.count()
        fake_group = Group.objects.create(
            description='Описание2',
            title='Имя2',
            slug='test-slug2'
        )

        form_data = {
            'text': 'Я терпеть не могу тестирование!',
            'group': fake_group.pk
        }

        response = self.guest_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostEditFormTests.post.pk}
            ),
            data=form_data,
            follow=True
        )

        self.assertRedirects(
            response,
            reverse(
                "posts:post_detail",
                kwargs={'post_id': PostEditFormTests.post.pk}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text='Я терпеть не могу тестирование!',
                author=PostEditFormTests.author_user,
                group=fake_group
            ).exists()
        )
        self.assertFalse(
            Post.objects.filter(
                text='Тестовый текст',
                author=PostCreateFormTests.author_user,
                group=PostEditFormTests.group
            ).exists()
        )
