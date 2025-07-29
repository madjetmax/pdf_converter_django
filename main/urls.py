from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_page, name='main_page'),
    path('check-task-status/<str:task_id>/<uuid:task_access_token>/', views.get_task_status, name='check_task_status'),
    path('download-file/<str:task_id>/<uuid:task_access_token>/', views.download_file, name='download_file'),
    # other
    path('questions/', views.questions_page, name='questions_page'),
    path('blog/', views.blog_page, name='blog_page'),
]
