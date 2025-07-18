from django.contrib import admin
from django.urls import path, include
from mentorship.views import home, login_view, register_view, find_mentors
from mentorship.views import my_requests, incoming_requests, accept_request, redirect_requests

# urlpatterns = [
#     path('', home, name='home'),
#     path('accounts/login/', login_view, name='login'),
#     path('accounts/register/', register_view, name='register'),
#     path('admin/', admin.site.urls),
#     path('requests/', redirect_requests),  # This redirects /requests/ to /my-requests/
#
#     path('mentors/', find_mentors, name='find_mentors'),
#     path('my-requests/', my_requests, name='my_requests'),
#     path('incoming-requests/', incoming_requests, name='incoming_requests'),
#     path('api/', include('mentorship.urls')),
#     path('requests/<int:request_id>/accept/', accept_request, name='accept_request'),

# ]
from django.contrib import admin
from django.urls import path
from mentorship.views import (
    home, login_view, register_view,
    find_mentors, my_requests, incoming_requests, accept_request, redirect_requests, logout_view
)

urlpatterns = [
    path('', home, name='home'),
    path('accounts/login/', login_view, name='login'),
    path('accounts/register/', register_view, name='register'),
    path('mentors/', find_mentors, name='find_mentors'),
    path('my-requests/', my_requests, name='my_requests'),
    path('incoming-requests/', incoming_requests, name='incoming_requests'),
    path('requests/', redirect_requests),
    path('accounts/logout/', logout_view, name='logout'),

    path('requests/<int:request_id>/accept/', accept_request, name='accept_request'),
    path('admin/', admin.site.urls),
]

