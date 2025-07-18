from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    home, login_view, edit_profile,
    book_session, session_feedback,
    RequestViewSet, AvailabilityViewSet, SessionViewSet, my_requests, incoming_requests,
    accept_request, find_mentors
)

router = DefaultRouter()
router.register('requests', RequestViewSet, basename='requests')
router.register('availability', AvailabilityViewSet, basename='availability')
router.register('sessions', SessionViewSet, basename='sessions')

urlpatterns = [
    # JWT auth endpoints
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Function-based views (template-based views)
    path('', home, name='home'),
    path('accounts/login/', login_view, name='login'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('sessions/book/', book_session, name='book_session'),
    path('my-requests/', my_requests, name='my_requests'),
    path('incoming-requests/', incoming_requests, name='incoming_requests'),
    path('mentors/', find_mentors, name='find_mentors'),
    path('requests/<int:request_id>/accept/', accept_request, name='accept_request'),
    path('sessions/<int:session_id>/feedback/', session_feedback, name='session_feedback'),

    # Include API ViewSets
    path('', include(router.urls)),
]
