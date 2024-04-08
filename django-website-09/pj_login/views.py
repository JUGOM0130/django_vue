from django.http import HttpResponse
from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

@login_required
def test_view(request):
    # セッションデータを確認
    session_data = request.session

    # セッションデータをログに出力
    print(session_data)
    keys = session_data.keys()
    print(keys)
    for k in keys:
        print("key : ",k)
    
    print('user_id\t',session_data.get('_auth_user_id'))
    print('backend\t',session_data.get('_auth_user_backend'))
    print('hash\t',session_data.get('_auth_user_hash'))

    print('CSRF_COOKIEの確認\t',request.META.get('CSRF_COOKIE'))

    return render(request,"registration/test.html")
    #return TemplateView.as_view(template_name="registration/test.html")


def test_vue_return(request):
    return render(request,"registration/vue.html")