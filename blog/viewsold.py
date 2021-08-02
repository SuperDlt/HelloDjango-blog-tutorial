from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse

# 它首先接受了一个名为 request 的参数，这个 request 就是 django 为我们封装好的 HTTP 请求，它是类 HttpRequest 的一个实例。
# 然后我们便直接返回了一个 HTTP 响应给用户，这个 HTTP 响应也是 django 帮我们封装好的，它是类 HttpResponse 的一个实例，只是我们给它传了一个自定义的字符串参数。
# def index(request):
#     return render(request, 'blog/index.html', context={
#         'title': '我的博客首页',
#         'welcome': '欢迎访问我的博客首页!'
#     })

# 模型管理器 objects 的使用。这里我们使用 all() 方法从数据库里获取了全部的文章，存在了 post_list 变量里。
# all 方法返回的是一个 QuerySet（可以理解成一个类似于列表的数据结构），由于通常来说博客文章列表是按文章发表时间倒序排列的，
# 即最新的文章排在最前面，所以我们紧接着调用了 order_by 方法对这个返回的 queryset 进行排序。
# 排序依据的字段是 created_time，即文章的创建时间。- 号表示逆序，如果不加 - 则是正序。
# 接着如之前所做，我们渲染了 blog\index.html 模板文件，并且把包含文章列表数据的 post_list 变量传给了模板。
from django.shortcuts import render
import markdown
from .models import Post, Category, Tag
from django.shortcuts import render, get_object_or_404
import re
from django.utils.text import slugify
from markdown.extensions.toc import TocExtension

def index(request):
    post_list = Post.objects.all().order_by('-created_time')
    return render(request, 'blog/index.html', context={'post_list': post_list})

# def detail(request, pk):
#     # get_object_or_404 方法，其作用就是当传入的 pk 对应的 Post 在数据库存在时，就返回对应的 post，
#     # 如果不存在，就给用户返回一个 404 错误，表明用户请求的文章不存在。
#     post = get_object_or_404(Post, pk=pk)
#     # markdown.markdown() 方法把 post.body 中的 Markdown 文本解析成了 HTML 文本。
#     # 同时我们还给该方法提供了一个 extensions 的额外参数。其中 markdown.extensions.toc 就是自动生成目录的拓展
#     post.body = markdown.markdown(post.body,
#                                   extensions=[
#                                       'markdown.extensions.extra',
#                                       'markdown.extensions.codehilite',
#                                       'markdown.extensions.toc',
#                                   ])
#     return render(request, 'blog/detail.html', context={'post': post})

# 在侧面生成一个目录
# def detail(request, pk):
#     post = get_object_or_404(Post, pk=pk)
#     md = markdown.Markdown(extensions=[
#         'markdown.extensions.extra',
#         'markdown.extensions.codehilite',
#         'markdown.extensions.toc',
#     ])
#     post.body = md.convert(post.body)
#     post.toc = md.toc
#
#     return render(request, 'blog/detail.html', context={'post': post})

# 在侧面生成一个目录，目录为空时不显示
# 这里我们正则表达式去匹配生成的目录中包裹在 ul 标签中的内容，如果不为空，说明目录存在，
# 就把 ul 标签中的值提取出来（目的是只要包含目录内容的最核心部分，多余的 HTML 标签结构丢掉）赋值给 post.toc；
# 否则，将 post 的 toc 置为空字符串，然后我们就可以在模板中通过判断 post.toc 是否为空，来决定是否显示侧栏目录：
def detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    md = markdown.Markdown(extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        # 记得在顶部引入 TocExtension 和 slugify
        TocExtension(slugify=slugify),
    ])
    post.body = md.convert(post.body)

    m = re.search(r'<div class="toc">\s*<ul>(.*)</ul>\s*</div>', md.toc, re.S)
    post.toc = m.group(1) if m is not None else ''

    return render(request, 'blog/detail.html', context={'post': post})

# 这里使用了模型管理器（objects）的 filter 方法来过滤文章。由于是按照日期归档，因此这里根据文章发表的年和月来过滤。
# 具体来说，就是根据 created_time 的 year 和 month 属性过滤，筛选出文章发表在对应的 year 年和 month 月的文章。
# 注意这里 created_time 是 Python 的 date 对象，其有一个 year 和 month 属性，我们在 页面侧边栏：使用自定义模板标签 使用过这个属性。
# Python 中调用属性的方式通常是 created_time.year，但是由于这里作为方法的参数列表，所以 django 要求我们把点替换成了两个下划线，即 created_time__year。同时和 index 视图中一样，我们对返回的文章列表进行了排序。此外由于归档页面和首页展示文章的形式是一样的，
def archive(request, year, month):
    post_list = Post.objects.filter(created_time__year=year,
                                    created_time__month=month
                                    ).order_by('-created_time')
    return render(request, 'blog/index.html', context={'post_list': post_list})

def category(request, pk):
    # 记得在开始部分导入 Category 类
    cate = get_object_or_404(Category, pk=pk)
    post_list = Post.objects.filter(category=cate).order_by('-created_time')
    return render(request, 'blog/index.html', context={'post_list': post_list})

def tag(request, pk):
    # 记得在开始部分导入 Tag 类
    t = get_object_or_404(Tag, pk=pk)
    post_list = Post.objects.filter(tags=t).order_by('-created_time')
    return render(request, 'blog/index.html', context={'post_list': post_list})

"""
当用户请求访问某篇文章时，处理该请求的视图函数为 detail 。一旦该视图函数被调用，说明文章被访问了一次，
因此我们修改 detail 视图函数，让被访问的文章在视图函数被调用时阅读量 +1。
"""
def detail(request, pk):
    post = get_object_or_404(Post, pk=pk)

    # 阅读量 +1
    post.increase_views()

    md = markdown.Markdown(extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        # 记得在顶部引入 TocExtension 和 slugify
        TocExtension(slugify=slugify),
    ])
    post.body = md.convert(post.body)

    m = re.search(r'<div class="toc">\s*<ul>(.*)</ul>\s*</div>', md.toc, re.S)
    post.toc = m.group(1) if m is not None else ''

    return render(request, 'blog/detail.html', context={'post': post})