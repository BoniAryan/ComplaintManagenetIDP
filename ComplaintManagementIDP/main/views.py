from django.shortcuts import render ,redirect, get_object_or_404
from django.http import HttpResponse
from .models import *
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from ComplaintManagementIDP import settings


def index(request):
    daak = {}
    return render(request, 'store/index.html',daak)

