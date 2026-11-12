from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic import TemplateView
from communications import views, bulletin_views, hierarchy_views, notification_views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('notificaciones/estado/', notification_views.notification_state, name='notification_state'),
    path('inbox/', views.inbox, name='inbox'),
    path('jerarquia/', hierarchy_views.hierarchy, name='hierarchy'),
    path('comunicados/', bulletin_views.bulletin_list, name='bulletin_list'),
    path('comunicados/nuevo/', bulletin_views.bulletin_create, name='bulletin_create'),
    path('comunicados/<int:pk>/', bulletin_views.bulletin_detail, name='bulletin_detail'),
    path('comunicados/<int:pk>/seguimiento/', bulletin_views.bulletin_tracking, name='bulletin_tracking'),
    path('comunicados/<int:pk>/seguimiento/csv/', bulletin_views.bulletin_tracking_csv, name='bulletin_tracking_csv'),
    path('comunicados/<int:pk>/confirmar/', bulletin_views.bulletin_confirm, name='bulletin_confirm'),
    path('chat/<int:user_id>/', views.chat, name='chat'),
]
