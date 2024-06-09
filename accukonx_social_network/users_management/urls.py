from django.urls import path, include
from .views import UserSignupView, CustomTokenObtainPairView, ProtectedView, search_users, FriendRequestViewSet, FriendViewSet, PendingFriendRequestsView, UnconnectedUsersView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'friend-requests', FriendRequestViewSet, basename='friend-request')
router.register(r'friends', FriendViewSet, basename='friend')

urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('search/', search_users, name='search_users'),
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('', include(router.urls)),
    path('pending-requests/', PendingFriendRequestsView.as_view(), name='pending_requests'),
    path('unconnected-users/', UnconnectedUsersView.as_view(), name='unconnected_users'),
    path('', include(router.urls)),
]
