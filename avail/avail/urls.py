"""
URL configuration for avail project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path,include

# swagger関連import
from rest_framework.schemas import get_schema_view
from django.views.generic import TemplateView

# Swaggerへ表示したいURLパターンを定義
api_patterns = [
    path('api4/', include('pdm4.urls')),  # 表示したいAPIのみ記述
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('pdm.urls')),
    path('api2/', include('pdm2.urls')),
    path('api3/', include('pdm3.urls')),
    path('api4/', include('pdm4.urls')),

    path('app/',include('entrypoint.urls')),
    path('login/',include('entrypoint.urls')),
    path("accounts/", include("accounts.urls")),
    
    # Swagger関連
    path('schema/', get_schema_view(          # スキーマ表示の追加
         title="API一覧",
         description="description",
         patterns=api_patterns,  # 表示したいパターンのみを指定
     ), name='openapi-schema'),
    path('docs/', TemplateView.as_view(       # ドキュメント表示の追加
        template_name='swagger-ui.html',
        extra_context={'schema_url':'openapi-schema'}
    ), name='swagger-ui'),
]
