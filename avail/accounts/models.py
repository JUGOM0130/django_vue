from django.db import models
import hashlib
from datetime import timedelta
from django.utils import timezone

# Create your models here.
class User(models.Model):
    user_id = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=20)
    comment = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.user_id} - {self.comment}"


    
def in_30_days():
    return timezone.now() + timedelta(days=30)

class AccessToken(models.Model):
    def __str__(self):
        return f"{self.user.user_id} - {self.token} - {self.access_datetime}"
    
    # ひもづくユーザー
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # アクセストークン(max_lengthが40に設定されている理由は、トークンはsha1でハッシュ化した文字列を設定するため)
    token = models.CharField(max_length=40)
    # アクセス日時
    access_datetime = models.DateTimeField(default=in_30_days)

    def str(self):
        # メールアドレスとアクセス日時、トークンが見えるように設定
        dt = timezone.localtime(self.access_datetime).strftime("%Y/%m/%d %H:%M:%S")
        return self.user.user_id + '(' + dt + ') - ' + self.token

    @staticmethod
    def create(user: User):
        # ユーザの既存のトークンを取得
        if AccessToken.objects.filter(user=user).exists():
            # トークンがすでに存在している場合は削除
            AccessToken.objects.get(user=user).delete()

        # トークン作成（UserID + Password + システム日付のハッシュ値とする）
        dt = timezone.now()
        str = user.user_id + user.password + dt.strftime('%Y%m%d%H%M%S%f')
        hash = hashlib.sha1(str.encode('utf-8')).hexdigest()

        # トークンをDBに追加
        token = AccessToken.objects.create(
            user=user,
            token=hash,
            access_datetime=dt)

        return token
    
    def token_check(token_str):
        if AccessToken.objects.filter(token=token_str).exists():
            # 存在した場合はトークンを返却
            return AccessToken.objects.get(token=token_str)
        else:
            # 存在しない場合はNoneを返却
            return None

    def check_valid_token(self):
        # このトークンが有効かどうかをチェック
        delta = timedelta(minutes=60)   # 有効時間は30分
        if(delta < timezone.now() - self.access_datetime):
            # 最終アクセス時間から30分以上経過している場合はFalseを返却
            return False
        return True

    def update_access_datetime(self):
        # 最終アクセス日時を現在日時で更新
        self.access_datetime = timezone.now()
        self.save()
        
        