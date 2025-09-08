from django.apps import AppConfig


class CodesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.pdm_system.codes'
    label = 'codes'  # この行を追加（アプリラベル）
    verbose_name = "コード管理機能"  # この行を追加（管理画面での表示名）
    
    #
    # python manage.py makemigrations codes
    # 本来 python manage.py apps.pdm_system.codes とすべきところを
    # codesとすることで、python manage.py makemigrations codes が可能になる
    #