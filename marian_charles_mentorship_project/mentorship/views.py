from rest_framework import viewsets, permissions
from .models import MentorshipRequest, Availability, Session, User, Profile
from .serializers import RequestSerializer, AvailabilitySerializer, SessionSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password


# ---------- Home View ----------

from django.contrib.auth import logout


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def home(request):
    if request.user.role == 'admin':
        return render(request, 'admin/dashboard.html')
    elif request.user.role == 'mentor':
        return render(request, 'mentor/dashboard.html')
    elif request.user.role == 'mentee':
        return render(request, 'mentee/dashboard.html')
    return render(request, 'base.html')  # fallback




User = get_user_model()

@login_required
def find_mentors(request):
    if request.user.role != 'mentee':
        return redirect('home')

    query = request.GET.get('q', '')
    mentors = User.objects.filter(role='mentor')

    if query:
        mentors = mentors.filter(
            Q(profile__skills__icontains=query) |
            Q(profile__bio__icontains=query)
        )

    if request.method == 'POST':
        mentor_id = request.POST.get('mentor_id')
        mentor = get_object_or_404(User, id=mentor_id)
        if not MentorshipRequest.objects.filter(mentee=request.user, mentor=mentor).exists():
            MentorshipRequest.objects.create(mentee=request.user, mentor=mentor)
        return redirect('find_mentors')

    return render(request, 'mentee/find_mentors.html', {
        'mentors': mentors,
        'query': query
    })



@login_required
def redirect_requests(request):
    return redirect('my_requests')  # This uses the URL name 'my_requests'


@login_required
def my_requests(request):
    if request.user.role != 'mentee':
        return redirect('home')
    requests = MentorshipRequest.objects.filter(mentee=request.user)
    return render(request, 'mentee/my_requests.html', {'requests': requests})


@login_required
def incoming_requests(request):
    if request.user.role != 'mentor':
        return redirect('home')
    requests = MentorshipRequest.objects.filter(mentor=request.user)
    return render(request, 'mentor/incoming_requests.html', {'requests': requests})


@login_required
def accept_request(request, request_id):
    if request.user.role != 'mentor':
        return redirect('home')
    req = get_object_or_404(MentorshipRequest, id=request_id, mentor=request.user)
    req.status = 'accepted'
    req.save()
    return redirect('incoming_requests')


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already taken'})

        user = User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            role=role,
        )
        return redirect('login')
    return render(request, 'register.html')


# ---------- Login View ----------
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')


# ---------- API ViewSets (JWT Protected) ----------
class RequestViewSet(viewsets.ModelViewSet):
    queryset = MentorshipRequest.objects.all()
    serializer_class = RequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'mentee':
            return user.sent_requests.all()
        if user.role == 'mentor':
            return user.received_requests.all()
        return MentorshipRequest.objects.none()

    @action(detail=True, methods=['put'])
    def accept(self, request, pk=None):
        req = self.get_object()
        req.status = 'accepted'
        req.save()
        return Response({'status': 'accepted'})


class AvailabilityViewSet(viewsets.ModelViewSet):
    serializer_class = AvailabilitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Availability.objects.filter(mentor=self.request.user)


class SessionViewSet(viewsets.ModelViewSet):
    serializer_class = SessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'mentor':
            return Session.objects.filter(request__mentor=user)
        return Session.objects.filter(request__mentee=user)


# ---------- HTML Template Views ----------
@login_required
def edit_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        profile.bio = request.POST.get('bio', '')
        profile.skills = request.POST.get('skills', '')
        profile.goals = request.POST.get('goals', '')
        profile.save()
        return redirect('home')
    return render(request, 'profile/edit.html', {'profile': profile})


@login_required
def book_session(request):
    mentors = User.objects.filter(role='mentor')
    if request.method == 'POST':
        mentor_id = request.POST.get('mentor')
        datetime_str = request.POST.get('datetime')
        mentor = User.objects.get(id=mentor_id)
        mentee = request.user
        session = Session.objects.create(
            request=None,  # You can link to a request if needed
            scheduled_time=timezone.datetime.fromisoformat(datetime_str),
        )
        return redirect('home')
    return render(request, 'sessions/book.html', {'mentors': mentors})


@login_required
def session_feedback(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    if request.method == 'POST':
        session.rating = request.POST.get('rating')
        session.feedback_mentee = request.POST.get('comment')
        session.save()
        return redirect('home')
    return render(request, 'sessions/feedback.html', {'session': session})


# ---------- Admin Role Management Views ----------
@login_required
def is_admin(user):
    return user.is_authenticated and user.role == 'admin'


@login_required
def manage_users(request):
    if not request.user.role == 'admin':
        return redirect('home')
    users = User.objects.all()
    return render(request, 'admin/manage_users.html', {'users': users})


@login_required
def update_user_role(request, user_id):
    if not request.user.role == 'admin':
        return redirect('home')
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        new_role = request.POST.get('role')
        if new_role in ['admin', 'mentor', 'mentee']:
            user.role = new_role
            user.save()
        return redirect('manage_users')
    return render(request, 'admin/update_user_role.html', {'user': user})
