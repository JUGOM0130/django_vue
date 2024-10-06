from django.contrib import admin
from .models import Code,CodeHeader,Tree,RootNode

# Register your models here.
admin.site.register(Code)

admin.site.register(CodeHeader)

admin.site.register(Tree)

admin.site.register(RootNode)