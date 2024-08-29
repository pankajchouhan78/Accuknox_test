from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from app import views

urlpatterns = [
    path("register/", views.RegisterView.as_view()),  # for user registration
    path("token/", TokenObtainPairView.as_view()),  # for user login
    path("token/refresh/", TokenRefreshView.as_view()),
    path("search/", views.SearchView.as_view()),
    # to send and reject and accept requests
    path("send_request/", views.SendFriendRequest.as_view()),
    path("accept_request/", views.AcceptRequestView.as_view()),
    path("reject_request/", views.RejectRequestView.as_view()),
    # API to list friends
    path("friend_list/", views.FriendListView.as_view()),
    # Retrieve Pending friend requests
    path("pending_requests/", views.PendingRequestView.as_view()),
]
