from django.contrib import admin
from django.urls import path
from bookingsystemapp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('booking/<int:place_id>/', views.details, name='details'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('profile/', views.profile, name='profile'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout, name='logout'),
    path('search/', views.search, name='search'),
    path('city/<slug:slug>/', views.city_search, name='city_search'),
    path('activate/<int:booking_id>/<str:token>/', views.activate_booking, name='activate_booking'),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)