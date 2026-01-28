from django.urls import path
from adm import views   

urlpatterns = [
    path('', views.signin, name='home'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('tournament/', views.tournament, name='tournament'),
    path('game/', views.game, name='game'),
    path('win/', views.win, name='win'),
    path('history/', views.history, name='history'),
    path('profile/', views.profile, name='profile'),
]

