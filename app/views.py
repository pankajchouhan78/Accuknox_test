from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Person
from .pagination import CustomPageNumberPagination
from .serializer import (
    AcceptRequestSerializer,
    PersonSerializer,
    RegisterSerializer,
    RejectRequestSerializer,
    SearchSerializer,
    SentRequestSerializer,
)


class RegisterView(APIView):

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)


class SearchView(APIView):

    def post(self, request):
        # import pdb;pdb.set_trace()
        serializer = SearchSerializer(data=request.data)
        if serializer.is_valid():
            search = serializer.data.get("search")
            try:
                person = Person.objects.filter(email=search)
            except Person.DoesNotExist:
                person = Person.objects.filter(Q(name__icontains=search))

            paginator = CustomPageNumberPagination()
            page = paginator.paginate_queryset(person, request)
            serializer = PersonSerializer(page, many=True)
            # check if search values are available
            if len(serializer.data) < 1:
                return Response("Couldn't find")
            return paginator.get_paginated_response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendFriendRequest(APIView):
    permission_classes = [IsAuthenticated]
    throttle_scope = "person"  # to set request limit

    def get(self, request):
        user = Person.objects.get(pk=request.user.pk)

        # Retrieve all relevant IDs
        old_sent_requests_list = [request.id for request in user.sent_requests.all()]
        old_received_requests_list = [
            request.id for request in user.received_requests.all()
        ]
        old_requests = old_sent_requests_list + old_received_requests_list
        friend_ids = [friend.id for friend in user.friends.all()]

        # Query for people who are not the user, friends, or have pending requests
        person = Person.objects.exclude(
            Q(id=request.user.id) | Q(id__in=friend_ids) | Q(id__in=old_requests)
        )
        serializer = PersonSerializer(person, many=True)

        if len(serializer.data) < 1:
            return Response("All Friends", status=200)
        return Response(serializer.data, status=200)

    def post(self, request):
        # Get authenticated user Id
        sender_id = request.user.id
        # Validate request data using serializer
        serializer = SentRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        # Get receiver_id from serializer
        receiver_id = serializer.data.get("to_request", None)

        # retrieve sender user by their id
        sender = Person.objects.get(pk=sender_id)
        # retrieve sender user's sender request and receiver request data
        sent_requests_list = [request.id for request in sender.sent_requests.all()]
        receive_request_list = [
            request.id for request in sender.received_requests.all()
        ]
        # check the receiver has Id
        if receiver_id is None:
            return Response("Please Enter Id")

        # check sender and receiver has different Ids
        if sender_id == receiver_id:
            return Response("both Person should be different")

        # check if request is already sent
        if receiver_id in sent_requests_list:
            return Response("Request Already Sent", status=404)

        # check if request is already in user's request list
        if receiver_id in receive_request_list:
            return Response("This User Already Requested You!", status=404)

        friends_list = [friend.id for friend in sender.friends.all()]
        # check if users are already friends
        if receiver_id in friends_list:
            return Response("Already Friends")

        try:
            # Get receiver object
            receiver = Person.objects.get(pk=receiver_id)
        except Person.DoesNotExist:
            return Response("Not Found", status=404)

        # add receiver request to sender's sent_reqeusts list
        sender.sent_requests.add(receiver_id)
        sender.save()
        # add sender request to receiver's sent_reqeusts list
        receiver.received_requests.add(sender_id)
        receiver.save()

        return Response("Request Has Been Sent", status=200)


class FriendListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get authenticated user object
        person = Person.objects.get(pk=request.user.id)
        # Get list of friends
        friends_list = person.friends.all()
        if len(friends_list) < 1:
            return Response("No friends", status=200)
        serializer = PersonSerializer(friends_list, many=True)
        return Response(serializer.data, status=200)


class PendingRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        person = Person.objects.get(id=request.user.id)
        # Retrieve all requests
        person_list = [request.id for request in person.received_requests.all()]

        # check if user has friends.
        if len(person_list) < 1:
            return Response(
                "User has no frind request", status=status.HTTP_400_BAD_REQUEST
            )

        person = Person.objects.filter(pk__in=person_list)
        serializer = PersonSerializer(person, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AcceptRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        receiver_id = request.user.id
        serializer = AcceptRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        sender_id = serializer.data.get("accept_request", None)

        if sender_id is None:
            return Response(
                "please provide a person_id", status=status.HTTP_400_BAD_REQUEST
            )

        if receiver_id == sender_id:
            return Response("both persons are Same", status=status.HTTP_400_BAD_REQUEST)

        try:
            sender = Person.objects.get(id=sender_id)
        except Person.DoesNotExist:
            return Response("Invalid User'Id", status=status.HTTP_400_BAD_REQUEST)

        user_list = [user.id for user in sender.friends.all()]
        if receiver_id in user_list:
            return Response(
                "this user is your friend", status=status.HTTP_400_BAD_REQUEST
            )

        # receiver user data
        if sender.sent_requests is None:
            return Response("No request", status=status.HTTP_400_BAD_REQUEST)

        data = [request.id for request in sender.sent_requests.all()]  # list of persons
        if receiver_id not in data:
            return Response(
                "There is no request assiated with this user",
                status=status.HTTP_400_BAD_REQUEST,
            )

        sender.sent_requests.remove(receiver_id)
        sender.friends.add(receiver_id)
        sender.save()

        # sender user data
        receiver = Person.objects.get(pk=receiver_id)
        receiver.received_requests.remove(sender_id)
        receiver.save()
        return Response("Request Accepted", status=200)


class RejectRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # import pdb;pdb.set_trace()
        receiver_id = request.user.id
        serializer = RejectRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        sender_id = serializer.data.get("reject_request", None)

        if sender_id is None:
            return Response(
                "Please provide a person_id", status=status.HTTP_400_BAD_REQUEST
            )

        if receiver_id == sender_id:
            return Response(
                "Both persons are the same", status=status.HTTP_400_BAD_REQUEST
            )

        try:
            sender = Person.objects.get(id=sender_id)
        except Person.DoesNotExist:
            return Response("Invalid User ID", status=status.HTTP_400_BAD_REQUEST)

        print([req.id for req in sender.sent_requests.all()])
        # Check if there's an incoming friend request from the sender to the receiver
        if receiver_id not in [req.id for req in sender.sent_requests.all()]:
            return Response(
                "There is no friend request associated with this user",
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Remove the friend request from the sender and receiver
        sender.sent_requests.remove(receiver_id)
        sender.save()

        receiver = Person.objects.get(pk=receiver_id)
        receiver.received_requests.remove(sender_id)
        receiver.save()

        return Response("Friend request rejected", status=status.HTTP_200_OK)
