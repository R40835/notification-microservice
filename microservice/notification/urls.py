from django.urls import path

from . import views

app_name = 'notification'

urlpatterns = [
    path('send-notification/', views.send_notification),
    path('user-notifications/', views.user_notifications),
]
