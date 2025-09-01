from django.urls import path
from django.contrib.auth import logout
from . import views

app_name = 'voting_app'
urlpatterns = [
    path('', views.login_view, name='login_view'),
    path('process_login', views.process_login,name='process_login'),
    path('register', views.register, name='register'),
    path('process_register', views.process_register, name='process_register'),
    path('vote_view', views.vote_view, name='vote_view'),
    path('vote_process', views.vote_process, name='vote_process'),
    path('submit_vote', views.submit_vote, name='submit_vote'),
    path('vote_success/', views.vote_success, name='vote_success'),
    path('already_voted/', views.already_voted, name='already_voted'),
    path('vote_result/', views.vote_result, name='vote_result'),
    path('admin_view', views.admin_view, name='admin_view'),
    path('admin_login', views.admin_login, name='admin_login'),
    path('view_admin', views.view_admin, name='view_admin'),
    path('edit/<int:candidate_id>', views.edit, name='edit'),
    path('process_edit/<int:candidate_id>', views.process_edit, name='process_edit'),
    path('voter_view', views.voter_view, name='voter_view'),
]
