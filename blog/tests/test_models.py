#存放和模型有关的单元测试
from django.apps import apps
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from blog.models import Post, Category


class PostModelTestCase(TestCase):
    def setUp(self):
        # 断开 haystack 的 signal，测试生成的文章无需生成索引
        # apps.get_app_config('haystack').signal_processor.teardown()
        user = User.objects.create_superuser(
            username='admin',
            email='admin@hellogithub.com',
            password='admin')
        cate = Category.objects.create(name='测试')
        self.post = Post.objects.create(
            title='测试标题',
            body='测试内容',
            category=cate,
            author=user,
        )

    def test_str_representation(self):
        self.assertEqual(self.post.__str__(), self.post.title)

    """
    这里我们要测试文章保存到数据库后，modifited_time 被正确设置了值（期待的值应该是文章保存时的时间）。
    self.assertIsNotNone(self.post.modified_time) 断言文章的 modified_time 不为空，说明的确设置了值。
    TestCase 类提供了系列 assert* 方法用于断言测试单元的逻辑结果是否和预期相符，一般从方法的命名中就可以读出其功能
    """
    def test_auto_populate_modified_time(self):
        self.assertIsNotNone(self.post.modified_time)

        old_post_modified_time = self.post.modified_time
        self.post.body = '新的测试内容'
        self.post.save()
        self.post.refresh_from_db()
        #修改文章内容，并重新保存数据库。预期的结果应该是，文章保存后，modifited_time 的值也被更新为修改文章时的时间，接下来的代码就是对这个预期结果的断言：
        self.assertTrue(self.post.modified_time > old_post_modified_time)

    def test_auto_populate_excerpt(self):
        self.assertIsNotNone(self.post.excerpt)
        self.assertTrue(0 < len(self.post.excerpt) <= 54)

    def test_get_absolute_url(self):
        expected_url = reverse('blog:detail', kwargs={'pk': self.post.pk})
        self.assertEqual(self.post.get_absolute_url(), expected_url)

    def test_increase_views(self):
        self.post.increase_views()
        self.post.refresh_from_db()
        self.assertEqual(self.post.views, 1)

        self.post.increase_views()
        self.post.refresh_from_db()
        self.assertEqual(self.post.views, 2)