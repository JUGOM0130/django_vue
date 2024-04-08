from django.contrib.auth.forms import UserCreationForm,AuthenticationForm

from .models import User,Fruit

from masta.models import FruitCategoryMasta

from django import forms

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "account_id",
            "email",
            "first_name",
            "last_name",
            "birth_date",
        )

# ログインフォームを追加
class LoginFrom(AuthenticationForm):
    class Meta:
        model = User


class RegistForm(forms.ModelForm):
    """ なぜかKEYが登録されてしまう。
    category = forms.ModelChoiceField(
        queryset=FruitCategoryMasta.objects.all(),
        label='カテゴリ',
        to_field_name='id',
    )
    """

    category = forms.ChoiceField(
        choices=[(d.id,d.category_name) for d in FruitCategoryMasta.objects.all()],
        label="カテゴリ"
    )

    class Meta:
        model = Fruit
        #fields = ['name', 'price', 'remarks','category']  # 作成フォームに表示するフィールド
        fields = '__all__'
