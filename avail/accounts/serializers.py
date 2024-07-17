from rest_framework import serializers
from .models import User


'''
登録
'''
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('user_id', 'password')
        extra_kwargs = {'password': {'write_only': True}}

        def create(self, validated_data):
            user = User.objects.create_user(**validated_data)
            return user

'''
ログイン
'''
class LoginSerializer(serializers.Serializer):
    user_id = serializers.CharField(max_length=255, write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    def validate(self, data):
        user_id = data.get('user_id')
        password = data.get('password')
        userid = User.objects.get(user_id=user_id)
        re_password = User.objects.get(password=password)
        if user_id == userid.user_id:
            if password == re_password.password:
                return data

            else:
                raise serializers.ValidationError('ログイン失敗')

'''
ユーザ情報更新
'''            
class UserUpdateSerializer(serializers.Serializer):
    comment = serializers.CharField(max_length=100, allow_blank=True)

    def update(self, instance, validated_data):
        instance.comment = validated_data.get('comment', instance.comment)
        instance.save()
        return instance