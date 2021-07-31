from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
import markdown
from django.utils.html import strip_tags

class Category(models.Model):
    """
    django 要求模型必须继承 models.Model 类。
    Category 只需要一个简单的分类名 name 就可以了。
    CharField 指定了分类名 name 的数据类型，CharField 是字符型，
    CharField 的 max_length 参数指定其最大长度，超过这个长度的分类名就不能被存入数据库。
    当然 django 还为我们提供了多种其它的数据类型，如日期时间类型 DateTimeField、整数类型 IntegerField 等等。
    django 内置的全部类型可查看文档：
    https://docs.djangoproject.com/en/2.2/ref/models/fields/#field-types
    """
    name = models.CharField(max_length=100)

    # 定义好 __str__ 方法后，解释器显示的内容将会是 __str__ 方法返回的内容。
    # 这里 Category 返回分类名 name ，Tag 返回标签名，而 Post 返回它的 title。
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = verbose_name


class Tag(models.Model):
    """
    标签 Tag 也比较简单，和 Category 一样。
    再次强调一定要继承 models.Model 类！
    """
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = verbose_name


class Post(models.Model):
    """
    文章的数据库表稍微复杂一点，主要是涉及的字段更多。
    """
    # body 是我们存储 Markdown 文本的字段：
    body = models.TextField()

    # 文章标题
    title = models.CharField('标题', max_length=70)

    # 文章正文，我们使用了 TextField。
    # 存储比较短的字符串可以使用 CharField，但对于文章的正文来说可能会是一大段文本，因此使用 TextField 来存储大段文本。
    body = models.TextField('正文')

    # 这两个列分别表示文章的创建时间和最后一次修改时间，存储时间的字段用 DateTimeField 类型。
    created_time = models.DateTimeField('创建时间', default=timezone.now)
    modified_time = models.DateTimeField('修改时间')

    # 文章摘要，可以没有文章摘要，但默认情况下 CharField 要求我们必须存入数据，否则就会报错。
    # 指定 CharField 的 blank=True 参数值后就可以允许空值了。
    excerpt = models.CharField('摘要', max_length=200, blank=True)

    # 这是分类与标签，分类与标签的模型我们已经定义在上面。
    # 我们在这里把文章对应的数据库表和分类、标签对应的数据库表关联了起来，但是关联形式稍微有点不同。
    # 我们规定一篇文章只能对应一个分类，但是一个分类下可以有多篇文章，所以我们使用的是 ForeignKey，即一
    # 对多的关联关系。且自 django 2.0 以后，ForeignKey 必须传入一个 on_delete 参数用来指定当关联的
    # 数据被删除时，被关联的数据的行为，我们这里假定当某个分类被删除时，该分类下全部文章也同时被删除，因此     # 使用 models.CASCADE 参数，意为级联删除。
    # 而对于标签来说，一篇文章可以有多个标签，同一个标签下也可能有多篇文章，所以我们使用
    # ManyToManyField，表明这是多对多的关联关系。
    # 同时我们规定文章可以没有标签，因此为标签 tags 指定了 blank=True。
    # 如果你对 ForeignKey、ManyToManyField 不了解，请看教程中的解释，亦可参考官方文档：
    # https://docs.djangoproject.com/en/2.2/topics/db/models/#relationships
    # 绝大部分 field 这个参数都位于第一个位置，但由于 ForeignKey、ManyToManyField 第一个参数必须传入其关联的 Model，
    # 所以 category、tags 这些字段我们使用了关键字参数 verbose_name。
    category = models.ForeignKey(Category,verbose_name='分类', on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, verbose_name='标签',blank=True)

    # 文章作者，这里 User 是从 django.contrib.auth.models 导入的。
    # django.contrib.auth 是 django 内置的应用，专门用于处理网站用户的注册、登录等流程，User 是
    # django 为我们已经写好的用户模型。
    # 这里我们通过 ForeignKey 把文章和 User 关联了起来。
    # 因为我们规定一篇文章只能有一个作者，而一个作者可能会写多篇文章，因此这是一对多的关联关系，和
    # Category 类似。
    author = models.ForeignKey(User,verbose_name='作者', on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    # 配置model的一些特性是通过model的内部类Meta中来定义。
    # 通过 verbose_name 来指定对应的 model 在 admin 后台的显示名称，这里 verbose_name_plural 用来表示多篇文章时的复数显示形式。
    # 英语中，如果有多篇文章，就会显示为 Posts，表示复数，中文没有复数表现形式，所以定义为和 verbose_name一样。
    class Meta:
        verbose_name = '文章'
        verbose_name_plural = verbose_name
        # django 允许我们在 models.Model 的子类里定义一个名为 Meta 的内部类，通过这个内部类指定一些属性的值来规定这个模型类该有的一些特性，
        # 例如在这里我们要指定 Post 的排序方式。首先看到 Post 的代码，在 Post 模型的内部定义的 Meta 类中，指定排序属性 ordering：
        ordering = ['-created_time']

    def save(self, *args, **kwargs):
        self.modified_time = timezone.now()

        # # 首先实例化一个 Markdown 类，用于渲染 body 的文本。
        # # 由于摘要并不需要生成文章目录，所以去掉了目录拓展。
        # md = markdown.Markdown(extensions=[
        #     'markdown.extensions.extra',
        #     'markdown.extensions.codehilite',
        # ])
        # #
        # # 先将 Markdown 文本渲染成 HTML 文本
        # # strip_tags 去掉 HTML 文本的全部 HTML 标签
        # # 从文本摘取前 54 个字符赋给 excerpt
        # self.excerpt = strip_tags(md.convert(self.body))[:54]

        super().save(*args, **kwargs)

    # 自定义 get_absolute_url 方法
    # 看到这个 reverse 函数，它的第一个参数的值是 'blog:detail'，意思是 blog 应用下的 name=detail 的函数，
    # 由于我们在上面通过 app_name = 'blog' 告诉了 django 这个 URL 模块是属于 blog 应用的，
    # 因此 django 能够顺利地找到 blog 应用下 name 为 detail 的视图函数，于是 reverse 函数会去解析这个视图函数对应的 URL，
    # 我们这里 detail 对应的规则就是 posts/<int:pk>/ int 部分会被后面传入的参数 pk 替换，
    # 所以，如果 Post 的 id（或者 pk，这里 pk 和 id 是等价的） 是 255 的话，
    # 那么 get_absolute_url 函数返回的就是 /posts/255/ ，这样 Post 自己就生成了自己的 URL。
    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'pk': self.pk})
