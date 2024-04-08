from django.contrib.auth import login, authenticate
from django.views.generic import TemplateView, CreateView,ListView
from django.contrib.auth.views import LoginView as BaseLoginView,  LogoutView as BaseLogoutView
from django.urls import reverse_lazy
from .forms import SignUpForm, LoginFrom, RegistForm
from .models import User,Fruit
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings

class IndexView(TemplateView):
    print("IndexView")
    template_name = "index.html"


class SignupView(CreateView):
    print("SignupView")
    form_class = SignUpForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("accounts:index")

    def form_valid(self, form):
        # login after signup
        response = super().form_valid(form)
        account_id = form.cleaned_data.get("account_id")
        password = form.cleaned_data.get("password1")
        user = authenticate(account_id=account_id, password=password)
        login(self.request, user)
        return response


class LoginView(BaseLoginView):
    print("LoginView")
    form_class = LoginFrom
    template_name = "accounts/login.html"


class LogoutView(BaseLogoutView):
    print("LogoutView")
    success_url = reverse_lazy("accounts:index")


# クラスベースビュー
# LoginRequiredMixin は、ログインしているか判定
class AccountInfoView(LoginRequiredMixin,TemplateView):

    # どのテンプレートを使うか
    template_name="accounts/account_info.html"

    # ログインされていなければリダイレクトするURLを
    login_url = reverse_lazy(settings.LOGIN_URL)  # ログインページのURLを指定

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ユーザーモデルをクエリしてユーザーオブジェクトを取得
        user = User.objects.filter(account_id=self.request.user.account_id)

        # ログ表示
        for u in user:
            print(u.account_id)
            print(u.email)
            print(u.first_name)
            print(u.last_name)
            print(u.birth_date)
            print(u.created_at)
            print(u.updated_at)

        # ユーザがいるかチェック
        if len(user) > 0:
            # 任意の変数を設定 ユーザがいる場合
            variable1 = 'ユーザ'
            variable2 = user[0].account_id
        else:
            # 任意の変数を設定　ユーザがいない場合
            variable1 = 'ユーザ'
            variable2 = 'がいません'

        # コンテキストに追加
        context['user'] = user
        context['variable1'] = variable1
        context['variable2'] = variable2


        return context



# フルーツ一覧を表示するクラスベースビュー
class FruitList(LoginRequiredMixin,ListView):
    model = Fruit
    template_name = "accounts/fruit_list.html"



class FruitCreateView(LoginRequiredMixin,CreateView):
    # 画面を表示するのに必要な情報↓
    model = Fruit
    '''
    form_classと併用はできない
    fields = ['name', 'price', 'remarks','category']  # 作成フォームに表示するフィールド
    '''
    template_name = "accounts/fruit_create.html"
    form_class = RegistForm

    # 登録処理をするのに必要な構文↓
    success_url = reverse_lazy('accounts:fruit_index')  # 登録後のリダイレクト先
    def form_valid(self, form):
        # フォームのデータを保存する前に何か特別な処理を追加する場合はここに記述
        return super().form_valid(form)


class Test(TemplateView):
    template_name = "vueindex.html"
