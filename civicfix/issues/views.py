from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import localtime
from .forms import IssueForm, RegisterForm
from .models import Issue, Profile, Department, StatusUpdate, STATUSES, CATEGORIES


def role(user):
    if not user.is_authenticated: return None
    p = getattr(user, "profile", None)
    return p.role if p else ("admin" if user.is_superuser else "citizen")


def scope(user):
    qs = Issue.objects.select_related("department", "reporter")
    r = role(user)
    if r == "admin": return qs
    if r == "officer": return qs.filter(department=user.profile.department)
    return qs.filter(reporter=user)


def ser(i):
    return {"id": i.id, "title": i.title, "category": i.get_category_display(), "status": i.status,
            "status_label": i.get_status_display(), "department": i.department.name if i.department else "",
            "address": i.address, "lat": i.latitude, "lng": i.longitude, "reporter": i.reporter.username,
            "created": localtime(i.created_at).strftime("%d %b %Y, %H:%M"), "url": f"/issue/{i.id}/"}


def stats(qs):
    s = {k: 0 for k, _ in STATUSES}
    s.update({r["status"]: r["n"] for r in qs.values("status").annotate(n=Count("id"))})
    s["total"] = sum(s.values())
    return s


def home(request):
    if not request.user.is_authenticated:  # first page = login / register
        return redirect("login")
    return render(request, "home.html", {"stats": stats(Issue.objects.all())})


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        user.email = form.cleaned_data["email"]
        user.save()
        Profile.objects.create(user=user, role="citizen")
        login(request, user, backend="issues.backends.EmailOrUsernameBackend")
        return redirect("dashboard")
    return render(request, "registration/form.html", {"form": form, "title": "Create your account", "cta": "Sign up"})


@login_required
def report(request):
    if role(request.user) != "citizen":
        messages.info(request, "Only citizen accounts can report issues.")
        return redirect("dashboard")
    form = IssueForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        issue = form.save(commit=False)
        issue.reporter = request.user
        issue.save()
        StatusUpdate.objects.create(issue=issue, status="assigned", by=request.user,
                                    note=f"Reported and routed to {issue.department}")
        messages.success(request, "Issue reported. You can follow its progress below.")
        return redirect("detail", pk=issue.pk)
    return render(request, "report.html", {"form": form})


@login_required
def dashboard(request):
    qs = scope(request.user)
    return render(request, "dashboard.html", {"role": role(request.user), "stats": stats(qs),
                  "statuses": STATUSES, "categories": CATEGORIES})


@login_required
def detail(request, pk):
    issue = get_object_or_404(scope(request.user), pk=pk)
    r = role(request.user)
    if request.method == "POST":
        if r == "citizen": return HttpResponseForbidden()
        status = request.POST.get("status")
        if status in dict(STATUSES):
            issue.status = status
            if r == "admin" and request.POST.get("department"):
                issue.department = get_object_or_404(Department, pk=request.POST["department"])
            issue.save()
            StatusUpdate.objects.create(issue=issue, status=status, by=request.user, note=request.POST.get("note", "")[:300])
            messages.success(request, "Status updated.")
        return redirect("detail", pk=pk)
    return render(request, "issue_detail.html", {"issue": issue, "role": r, "statuses": STATUSES,
                  "departments": Department.objects.all(), "updates": issue.updates.select_related("by")})


def api_issues(request):
    if request.GET.get("public"):
        qs = Issue.objects.select_related("department", "reporter")
    elif request.user.is_authenticated:
        qs = scope(request.user)
    else:
        return JsonResponse({"error": "login required"}, status=401)
    allqs = qs
    for f in ("status", "category"):
        if request.GET.get(f): qs = qs.filter(**{f: request.GET[f]})
    return JsonResponse({"stats": stats(allqs), "issues": [ser(i) for i in qs[:200]]})


@login_required
def api_issue(request, pk):
    issue = get_object_or_404(scope(request.user), pk=pk)
    ups = [{"status": u.get_status_display(), "key": u.status, "note": u.note, "by": u.by.username if u.by else "system",
            "at": localtime(u.created_at).strftime("%d %b, %H:%M")} for u in issue.updates.select_related("by")]
    return JsonResponse({**ser(issue), "updates": ups})