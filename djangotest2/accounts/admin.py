from django.contrib import admin
from django.contrib.auth.models import Group

from .models import User,Fruit


#admin.site.register(User, UserAdmin)  # UserAdminが謎なのでコメントアウト下記に書き換え
admin.site.register(User)  # Userモデルを登録


admin.site.unregister(Group)  # Groupモデルは不要のため非表示にします




admin.site.register(Fruit)  # Userモデルを登録
