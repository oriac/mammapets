from django.urls import path

from . import views

app_name = 'web'
urlpatterns = [
    path('', views.index, name='index'),
    # ex: /polls/5/
    path('<int:pet_id>/', views.detail, name='detail'),
    path('contract/', views.contract, name='contract'),
    path('new_contract/', views.new_contract, name='new_contract'),
    path('profiles/<int:user_id>/', views.user_profile, name='user_profile'),
    path('contract/<int:contract_id>/add_log/', views.add_pet_care_log, name='add_pet_care_log'),
]