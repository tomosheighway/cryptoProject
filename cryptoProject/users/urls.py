from django.urls import path
from . import views
from django.contrib.auth import views as auth_view

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('graphs/', views.graphs, name='graphs'),
    path('bitcoin-chart/', views.bitcoin_chart, name='bitcoin_chart'),
    # path('ethereum-chart/', views.ethereum_chart, name='ethereum_chart'),
    path('login/', auth_view.LoginView.as_view(template_name='users/login.html'), name="login"),
    path('logout/', auth_view.LogoutView.as_view(template_name='users/logout.html'), name="logout"),
    
    
    
]

   