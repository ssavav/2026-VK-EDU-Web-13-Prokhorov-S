from django.urls import path
from . import views

urlpatterns =[
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='settings'),
    path('logout/', views.logout_view, name='logout'),
    path('user/<str:username>/', views.public_profile, name='public_profile'),
    path("dyn-test/", views.dyn_test, name="dyn_test"),
]