from django.contrib import admin
from .models import Prefix,Code,CodeVersion,CodeChangeLog,CodeMetadata


# Register your models here.
admin.site.register(Prefix)

admin.site.register(Code)

admin.site.register(CodeVersion)

admin.site.register(CodeChangeLog)

admin.site.register(CodeMetadata)