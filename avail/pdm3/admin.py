from django.contrib import admin
from .models import Node,Tree,TreeStructure,TreeVersion,Prefix,CodeCounter,CodeVersion,CodeVersionHistory

models = [Node,Tree,TreeStructure,TreeVersion,Prefix,CodeCounter,CodeVersion,CodeVersionHistory]

# Register your models here.
admin.site.register(models)
