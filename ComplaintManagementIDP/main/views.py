from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Citizen, Department, Complaint, ComplaintLog, Feedback
from .forms import CitizenRegistrationForm, DepartmentRegistrationForm, ComplaintForm, ComplaintLogForm, FeedbackForm
from .nlp_utils import preprocess_text, categorize_complaint, assign_priority
from django.shortcuts import redirect


def index(request):
    """Home page"""
    return render(request, 'main/index.html')


# Citizen Views
def citizen_register(request):
    if request.method == 'POST':
        form = CitizenRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! Please login.')
            return redirect('main:citizen_login')
    else:
        form = CitizenRegistrationForm()
    return render(request, 'main/citizen_register.html', {'form': form})


def citizen_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None and hasattr(user, 'citizen'):
            login(request, user)
            return redirect('main:citizen_dashboard')
        else:
            messages.error(request, 'Invalid credentials or not a citizen account.')

    return render(request, 'main/citizen_login.html')


@login_required
def citizen_dashboard(request):
    """Citizen dashboard showing their complaints"""
    if not hasattr(request.user, 'citizen'):
        messages.error(request, 'Access denied.')
        return redirect('main:index')

    citizen = request.user.citizen
    complaints = citizen.complaints.all()

    # Add latest status to each complaint
    for complaint in complaints:
        complaint.latest_status = complaint.get_latest_status()
        complaint.latest_remarks = complaint.get_latest_remarks()

    context = {
        'citizen': citizen,
        'complaints': complaints
    }
    return render(request, 'main/citizen_dashboard.html', context)


@login_required
def register_complaint(request):
    """Register a new complaint"""
    if not hasattr(request.user, 'citizen'):
        messages.error(request, 'Access denied.')
        return redirect('main:index')

    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.citizen = request.user.citizen

            # Process with NLP
            processed_text = preprocess_text(complaint.description)
            category, department = categorize_complaint(processed_text)
            priority = assign_priority(processed_text)

            complaint.category = category
            complaint.department = department
            complaint.priority = priority
            complaint.save()

            # Handle multiple image uploads
            images = request.FILES.getlist('images')
            if images:
                # For now, we'll just save the first image since the model has single ImageField
                # You can modify this logic based on your needs
                complaint.images = images[0]
                complaint.save()

            messages.success(request, 'Complaint registered successfully!')
            return redirect('main:citizen_dashboard')
    else:
        form = ComplaintForm()

    return render(request, 'main/register_complaint.html', {'form': form})


@login_required
def view_complaint(request, complaint_id):
    """View detailed complaint information"""
    complaint = get_object_or_404(Complaint, id=complaint_id)

    # Check if user has permission to view this complaint
    if hasattr(request.user, 'citizen') and complaint.citizen != request.user.citizen:
        messages.error(request, 'Access denied.')
        return redirect('main:citizen_dashboard')

    logs = complaint.logs.all()

    context = {
        'complaint': complaint,
        'logs': logs
    }
    return render(request, 'main/view_complaint.html', context)


@login_required
def submit_feedback(request, complaint_id):
    """Submit feedback for a complaint"""
    complaint = get_object_or_404(Complaint, id=complaint_id)

    if not hasattr(request.user, 'citizen') or complaint.citizen != request.user.citizen:
        messages.error(request, 'Access denied.')
        return redirect('main:citizen_dashboard')

    if hasattr(complaint, 'feedback'):
        messages.warning(request, 'Feedback already submitted for this complaint.')
        return redirect('main:citizen_dashboard')

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.complaint = complaint
            feedback.save()
            messages.success(request, 'Thank you for your feedback!')
            return redirect('main:citizen_dashboard')
    else:
        form = FeedbackForm()

    context = {
        'complaint': complaint,
        'form': form
    }
    return render(request, 'main/feedback_form.html', context)


# Department Views
def department_register(request):
    if request.method == 'POST':
        form = DepartmentRegistrationForm(request.POST)
        if form.is_valid():
            department = form.save()
            messages.success(request, 'Department registration successful! Please login.')
            return redirect('main:department_login')
    else:
        form = DepartmentRegistrationForm()
    return render(request, 'main/department_register.html', {'form': form})


def department_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            try:
                department = Department.objects.get(user=user)
                login(request, user)
                return redirect('main:department_dashboard')
            except Department.DoesNotExist:
                messages.error(request, 'Not a department account.')
        else:
            messages.error(request, 'Invalid credentials.')

    return render(request, 'main/department_login.html')


# @login_required
# def department_dashboard(request):
#     """Department dashboard for managing complaints"""
#     try:
#         department = Department.objects.get(user=request.user)
#     except Department.DoesNotExist:
#         messages.error(request, 'Access denied.')
#         return redirect('main:index')
#
#     # Filter complaints by status
#     status_filter = request.GET.get('status', 'all')
#     complaints = department.complaints.all()
#
#     if status_filter != 'all':
#         complaints = complaints.filter(logs__status=status_filter).distinct()
#
#     # Sort by priority
#     priority_order = {'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
#     complaints = sorted(complaints, key=lambda x: priority_order.get(x.priority, 4))
#
#     # Add latest status to each complaint
#     for complaint in complaints:
#         complaint.latest_status = complaint.get_latest_status()
#         complaint.latest_remarks = complaint.get_latest_remarks()
#
#     context = {
#         'department': department,
#         'complaints': complaints,
#         'status_filter': status_filter
#     }
#     return render(request, 'main/department_dashboard.html', context)


@login_required
def department_dashboard(request):
    """Department dashboard for managing complaints"""
    try:
        department = Department.objects.get(user=request.user)
    except Department.DoesNotExist:
        messages.error(request, 'Access denied.')
        return redirect('main:index')

    # Filter complaints by status
    status_filter = request.GET.get('status', 'all')
    complaints = department.complaints.all()

    if status_filter != 'all':
        complaints = complaints.filter(logs__status=status_filter).distinct()

    # Sort by priority
    priority_order = {'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
    complaints = sorted(complaints, key=lambda x: priority_order.get(x.priority, 4))

    # Add latest status to each complaint
    for complaint in complaints:
        complaint.latest_status = complaint.get_latest_status()
        complaint.latest_remarks = complaint.get_latest_remarks()

    # Calculate performance statistics
    all_complaints = department.complaints.all()
    total_complaints = all_complaints.count()

    # Count resolved complaints
    resolved_complaints = 0
    pending_complaints = 0

    for complaint in all_complaints:
        latest_status = complaint.get_latest_status()
        if latest_status == 'Resolved':
            resolved_complaints += 1
        elif latest_status in ['In-progress', 'Pending']:
            pending_complaints += 1

    # Calculate average rating from feedback
    feedbacks = Feedback.objects.filter(complaint__department=department)
    if feedbacks.exists():
        total_rating = sum(feedback.rating for feedback in feedbacks)
        average_rating = total_rating / feedbacks.count()
    else:
        average_rating = 0

    context = {
        'department': department,
        'complaints': complaints,
        'status_filter': status_filter,
        'total_complaints': total_complaints,
        'resolved_complaints': resolved_complaints,
        'pending_complaints': pending_complaints,
        'average_rating': average_rating,
    }
    return render(request, 'main/department_dashboard.html', context)
@login_required
def update_complaint_status(request, complaint_id):
    """Update complaint status"""
    complaint = get_object_or_404(Complaint, id=complaint_id)

    try:
        department = Department.objects.get(user=request.user)
        if complaint.department != department:
            messages.error(request, 'Access denied.')
            return redirect('main:department_dashboard')
    except Department.DoesNotExist:
        messages.error(request, 'Access denied.')
        return redirect('main:index')

    if request.method == 'POST':
        form = ComplaintLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.complaint = complaint
            log.save()
            messages.success(request, 'Status updated successfully!')
            return redirect('main:department_dashboard')

    return redirect('main:department_dashboard')
def logout_view(request):
    logout(request)
    return redirect('main:index')  # Replace 'login' with the name of your login URL