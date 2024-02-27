from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView


# TemplateViewは今までviews.pyにちゃんとコードを書いて作っていたが、テンプレートを一つ表示するだけなら以下でOK
index_view = TemplateView.as_view(template_name="registration/index.html")

urlpatterns = [
    path('admin/', admin.site.urls),
    # index_viewはログインしないと見れない
    path("", login_required(index_view), name="index"),
    # もしもdjangoが元々用意しているurlにマッチしたらそっちを表示する、という意味
    # マッチしなければトップページを表示する(index_view)
    # ここの「urls」の中には、ログイン、ログアウト、パスワード変更、パスワードリセット等が含まれている
    path('', include("django.contrib.auth.urls")),
]
