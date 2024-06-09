from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, login
from rest_framework import viewsets, permissions
from .models import FriendRequest, Friend
from .serializers import FriendRequestSerializer, FriendSerializer
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from .serializers import UserSignupSerializer, FriendRequestSerializer, FriendSerializer, UserSerializer

User = get_user_model()

class UserSignupView(generics.CreateAPIView):
    serializer_class = UserSignupSerializer
    permission_classes = [AllowAny]

class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)

class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "This is a protected view. You are authenticated."})
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_users(request):
    query = request.GET.get('query', '')
    if query:
        if '@' in query:
            users = User.objects.filter(email__iexact=query)
        else:
            users = User.objects.filter(username__icontains=query)
    else:
        users = User.objects.none()

    user_data = [{"id": user.id, "username": user.username, "email": user.email} for user in users]
    return Response(user_data)

class FriendRequestThrottle(UserRateThrottle):
    rate = '3/min'

class FriendRequestViewSet(viewsets.ModelViewSet):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [FriendRequestThrottle]

    def get_queryset(self):
        if self.action == 'list':
            return self.queryset.filter(to_user=self.request.user)
        return self.queryset

    def perform_create(self, serializer):
        from_user = self.request.user
        to_user = serializer.validated_data.get('to_user')

        # if a friend request already exists
        existing_request = FriendRequest.objects.filter(
            Q(from_user=from_user, to_user=to_user) |
            Q(from_user=to_user, to_user=from_user),
            status='pending'
        ).first()

        if existing_request:
            return Response({'status': 'failure', 'message': 'Friend request already sent'}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(from_user=from_user)

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def accept(self, request, pk=None):
        friend_request = self.get_object()

        if friend_request.status != 'pending':
            return Response({'status': 'failure', 'message': 'Only pending requests can be accepted'}, status=status.HTTP_400_BAD_REQUEST)

        friend_request.status = 'accepted'
        friend_request.save()
        try:
            Friend.make_friend(request.user, friend_request.from_user)
            Friend.make_friend(friend_request.from_user, request.user)
        except Exception as e:
            print('error---------making friend',e)

        return Response({'status': 'success', 'message': 'Friend request accepted'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def reject(self, request, pk=None):
        friend_request = self.get_object()

        if friend_request.status != 'pending':
            return Response({'status': 'failure', 'message': 'Only pending requests can be rejected'}, status=status.HTTP_400_BAD_REQUEST)

        friend_request.status = 'rejected'
        friend_request.save()
        return Response({'status': 'success', 'message': 'Friend request rejected'}, status=status.HTTP_200_OK)


class FriendViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FriendSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # print(user,'------------1816')
        return Friend.objects.filter(current_user=user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # print(queryset,'------------116')
        serializer = self.get_serializer(queryset, many=True)
        return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)

class PendingFriendRequestsView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FriendRequest.objects.filter(to_user=self.request.user, status='pending')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)

class UnconnectedUsersPagination(PageNumberPagination):
    page_size = 10

class UnconnectedUsersView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = UnconnectedUsersPagination

    def get_queryset(self):
        user = self.request.user
        connected_users = Friend.objects.filter(users=user).values_list('users', flat=True)
        return User.objects.exclude(id__in=connected_users).exclude(id=user.id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({'status': 'success', 'data': serializer.data})

        serializer = self.get_serializer(queryset, many=True)
        return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)