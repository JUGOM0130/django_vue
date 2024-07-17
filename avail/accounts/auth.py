from django.contrib.auth.models import User
from rest_framework import authentication
from rest_framework import exceptions
from rest_framework import status
from .models import AccessToken

class ExampleAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        # リクエストヘッダからトークン文字列を取得
        # token_str = request.META.get('HTTP_X_AUTH_TOKEN')デフォルトはこれだけどMETAがよくわからんのでheaderを使うことに
        token_str = request.headers.get('My-Token')
        if not token_str:
            # リクエストヘッダにトークンが含まれない場合はエラー
            raise exceptions.AuthenticationFailed({'message': 'token injustice.'})

        # トークン文字列からトークンを取得する
        token = AccessToken.token_check(token_str)
        if token == None:
            # トークンが取得できない場合はエラー
            raise exceptions.AuthenticationFailed({'message': 'Token not found.'})

        # トークンが取得できた場合は、有効期間をチェック
        if not token.check_valid_token():
            # 有効期限切れの場合はエラー
            raise exceptions.AuthenticationFailed({'message': 'Token expired.'})

        # トークンが有効な場合は、アクセス日時を更新
        token.update_access_datetime()

        return (token.user, None)
