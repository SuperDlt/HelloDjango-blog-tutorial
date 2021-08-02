import os
import pathlib
import random
import sys
from datetime import timedelta

import django
import faker
from django.utils import timezone

# 将项目根目录添加到 Python 的模块搜索路径中
back = os.path.dirname
BASE_DIR = back(back(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blogproject.settings.local")
    django.setup()

    # 这是整个脚本最为重要的部分。首先设置 DJANGO_SETTINGS_MODULE 环境变量，这将指定 django 启动时使用的配置文件，然后运行 django.setup() 启动 django。
    # 这是关键步骤，只有在 django 启动后，我们才能使用 django 的 ORM 系统。django 启动后，就可以导入各个模型，以便创建数据。
    from blog.models import Category, Post, Tag
    from comments.models import Comment
    from django.contrib.auth.models import User
    # 这一段脚本用于清除旧数据，因此每次运行脚本，都会清除原有数据，然后重新生成。
    print('clean database')
    Post.objects.all().delete()
    Category.objects.all().delete()
    Tag.objects.all().delete()
    Comment.objects.all().delete()
    User.objects.all().delete()
    print('create a blog user')
    user = User.objects.create_superuser('admin', 'admin@hellogithub.com', 'admin')

    category_list = ['Python学习笔记', '开源项目', '工具资源', '程序员生活感悟', 'test category']
    tag_list = ['django', 'Python', 'Pipenv', 'Docker', 'Nginx', 'Elasticsearch', 'Gunicorn', 'Supervisor', 'test tag']
    a_year_ago = timezone.now() - timedelta(days=365)

    print('create categories and tags')
    for cate in category_list:
        Category.objects.create(name=cate)

    for tag in tag_list:
        Tag.objects.create(name=tag)

    print('create a markdown sample post')
    Post.objects.create(
        title='Markdown 与代码高亮测试',
        body=pathlib.Path(BASE_DIR).joinpath('scripts', 'md.sample').read_text(encoding='utf-8'),
        category=Category.objects.create(name='Markdown测试'),
        author=user,
    )
    # 这个脚本没什么说的，简单地使用 django 的 ORM API 生成博客用户、分类、标签以及一篇 Markdown 测试文章。
    print('create some faked posts published within the past year')
    fake = faker.Faker()  # English
    # 这段脚本用于生成 100 篇英文博客文章。博客文章通常内容比较长，因此我们使用了之前提及的 Faker 库来自动生成文本内容。
    for _ in range(100):
        tags = Tag.objects.order_by('?')
        tag1 = tags.first()
        tag2 = tags.last()
        cate = Category.objects.order_by('?').first()
        created_time = fake.date_time_between(start_date='-1y', end_date="now",
                                              tzinfo=timezone.get_current_timezone())
        post = Post.objects.create(
            title=fake.sentence().rstrip('.'),
            body='\n\n'.join(fake.paragraphs(10)),
            created_time=created_time,
            category=cate,
            author=user,
        )
        post.tags.add(tag1, tag2)
        post.save()
    #这一段脚本和上一段几乎完全一样，唯一不同的是构造 Faker 实例时，传入了一个语言代码 zh_CN，这将生成中文的虚拟数据，而不是默认的英文。
    fake = faker.Faker('zh_CN')
    for _ in range(100):  # Chinese
        tags = Tag.objects.order_by('?')
        tag1 = tags.first()
        tag2 = tags.last()
        cate = Category.objects.order_by('?').first()
        created_time = fake.date_time_between(start_date='-1y', end_date="now",
                                              tzinfo=timezone.get_current_timezone())
        post = Post.objects.create(
            title=fake.sentence().rstrip('.'),
            body='\n\n'.join(fake.paragraphs(10)),
            created_time=created_time,
            category=cate,
            author=user,
        )
        post.tags.add(tag1, tag2)
        post.save()
