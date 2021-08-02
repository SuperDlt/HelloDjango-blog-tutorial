"""blogproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from django.contrib import admin
from django.urls import path, include

from blog.feeds import AllPostsRssFeed

"""
django 匹配 URL 模式是在 blogproject 目录（即 settings.py 文件所在的目录）的 urls.py 下的，
所以我们要把 blog 应用下的 urls.py 文件包含到 blogproject\ urls.py 里去，
"""
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
    path('', include('comments.urls')),

    path('all/rss/', AllPostsRssFeed(), name='rss'),
]
