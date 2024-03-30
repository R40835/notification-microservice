from django.urls import path

from . import views

app_name = 'notification'

urlpatterns = [
    path('send-blog-notification/', views.send_blog_notification),
    path('send-event-notification/', views.send_event_notification),
    path('user-notifications/', views.user_notifications),
]
