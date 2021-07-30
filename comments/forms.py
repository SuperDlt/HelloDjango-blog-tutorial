# 在 comments 目录下（和 models.py 同级）新建一个 forms.py 文件，用来存放表单代码
from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'url', 'text']