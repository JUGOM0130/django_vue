from django.shortcuts import render
from django.contrib.auth.models import User
from django.http.response import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated       # 追加
from accounts.auth import ExampleAuthentication            # 追加

import json

class LoginViewClass(APIView):
    def get(self, request, format=None):
        return render(request, 'login.html')

class TreeViewClass(APIView):
    authentication_classes = (ExampleAuthentication,)        # 追加
    # permission_classes = (IsAuthenticated,)                  # 追加

    def get(self, request, format=None):
        #return JsonResponse({'message': 'Yes'})
        return render(request, 'tree.html')