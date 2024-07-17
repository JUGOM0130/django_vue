# 参考サイト
https://zenn.dev/iccyan/articles/66e0245c854137

# ログインユーザ作成
http://127.0.0.1:8081/accounts/signup/
```
{'user_id': 'user1', 'password': 'junnsann1', 'password_confirmation': 'junnsann1'}
```

# ログイン
http://127.0.0.1:8081/accounts/login/
* ログインすると↓
* response
```
{
    "detail": "ログインが成功しました。",
    "error": 0,
    "token": "4ddcfc6e5ff606f1cd47c3d3d54ab7f4614913fe",
    "user_id": "user1"
}
```