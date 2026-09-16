from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import OrderingFilter, SearchFilter

from .models import Task
from .serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "updated_at", "due_date", "priority"]
    ordering = ["status", "-updated_at"]

    def get_queryset(self):
        queryset = super().get_queryset().filter(owner=self.request.user)
        status = self.request.query_params.get("status")
        if status in {choice.value for choice in Task.Status}:
            queryset = queryset.filter(status=status)
        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


@login_required
def index(request):
    current_time = timezone.localtime()
    if current_time.hour < 12:
        greeting = "Good morning"
    elif current_time.hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    return render(
        request,
        "tasks/index.html",
        {
            "greeting": greeting,
            "current_date": f"{current_time:%A, %B} {current_time.day}",
        },
    )


def register(request):
    if request.user.is_authenticated:
        return redirect("index")

    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("index")

    return render(request, "registration/register.html", {"form": form})