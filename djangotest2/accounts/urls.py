from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path('signup/', views.SignupView.as_view(), name="signup"),
    path('login/', views.LoginView.as_view(), name="login"),
    path('logout/', views.LogoutView.as_view(), name="logout"),
    path('account_info/', views.AccountInfoView.as_view(), name="account_info"),

    path('fruit/',views.FruitList.as_view(),name='fruit_index'),
    path('fruit/create/',views.FruitCreateView.as_view(),name='fruit_create'),

    path('test/',views.Test.as_view(),name="test"),

]
