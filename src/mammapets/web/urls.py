from django.urls import path

from . import views

app_name = 'web'
urlpatterns = [
    path('', views.index, name='index'),
    # ex: /polls/5/
    path('<int:pet_id>/', views.detail, name='detail'),
    # ex: /polls/5/results/
    path('<int:pet_id>/results/', views.results, name='results'),
    # ex: /polls/5/vote/
    path('<int:pet_id>/vote/', views.vote, name='vote'),
    path('contract/', views.contract, name='contract'),
    path('new_contract/', views.new_contract, name='new_contract'),
    path('profiles/<int:user_id>/', views.user_profile, name='user_profile'),
]