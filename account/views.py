from django.shortcuts import render
from rest_framework.generics import CreateAPIView
# Create your views here.

from .models import User
from .serializers import RegisterSerializer


class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


