# プロジェクト作成
```cmd
//プロジェクト作成
django-admin startproject project

cd project

//アプリケーション作成
python manage.py startapp application

//マイグレーションファイル作成
python manage.py makemigrations

//マイグレーション実行
python manage.py migrate

//superuser作成
python manage.py createsuperuser
//root
//syssui

```
# クラスベースビュー、関数ベースビュー
* 基本はクラスベースビューを使う方がいいみたい

# shellを使ってモデルクラスの操作

```cmd
python manage.py shell

//モデルクラスへのアクセス
from fruits.models model import FruitsModel

obj = FruitsModel(name='banana')

obj.name

obj.save()

```
