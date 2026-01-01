from http.client import responses

from .serializers import UserSerializer
from rest_framework import generics
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class protected_view(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        response = {
            'status': 'Request was permitted'
        }
        return Response(response)