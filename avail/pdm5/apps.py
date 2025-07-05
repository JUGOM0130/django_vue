# avail/pdm5/apps.py
"""
Django アプリ設定
シグナルの登録を行い、自動同期機能を有効化
"""

from django.apps import AppConfig

class Pdm5Config(AppConfig):
    """
    PDM5アプリケーション設定
    共有構造の自動同期機能を含む
    """
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pdm5'
    verbose_name = '共有ツリー構造システム（PDM5）'
    
    def ready(self):
        """
        アプリケーション初期化時に実行される
        シグナルハンドラーを登録して自動同期機能を有効化
        """
        
        try:
            # シグナルハンドラーを登録
            from . import signals
            signals.register_signals()
            
            # ログ設定
            import logging
            logger = logging.getLogger(__name__)
            logger.info("PDM5: 共有構造自動同期機能が有効化されました")
            
        except ImportError as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"PDM5: シグナル登録に失敗しました: {e}")


