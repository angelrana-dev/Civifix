from django.contrib.auth.models import User
from django.db import models

CATEGORIES = [("garbage", "Garbage overflow"), ("streetlight", "Broken streetlight"),
              ("road", "Road damage"), ("water", "Water leakage"), ("other", "Other")]
STATUSES = [("assigned", "Assigned"), ("in_progress", "In progress"), ("resolved", "Resolved"), ("rejected", "Rejected")]
DEPT_FOR = {"garbage": "Sanitation", "streetlight": "Electrical", "road": "Roads & Public Works",
            "water": "Water Supply", "other": "General Administration"}


class Department(models.Model):
    name = models.CharField(max_length=80, unique=True)
    def __str__(self): return self.name


class Profile(models.Model):
    ROLES = [("citizen", "Citizen"), ("officer", "Officer"), ("admin", "Admin")]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=10, choices=ROLES, default="citizen")
    department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.SET_NULL)
    def __str__(self): return f"{self.user.username} ({self.role})"


class Issue(models.Model):
    title = models.CharField(max_length=140)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORIES)
    photo = models.ImageField(upload_to="issues/", blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUSES, default="assigned")
    department = models.ForeignKey(Department, null=True, on_delete=models.SET_NULL, related_name="issues")
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="issues")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta: ordering = ["-created_at"]

    def save(self, *a, **kw):
        if not self.department_id:  # auto-route to the right department
            self.department, _ = Department.objects.get_or_create(name=DEPT_FOR[self.category])
        super().save(*a, **kw)

    def __str__(self): return f"#{self.pk} {self.title}"


class StatusUpdate(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name="updates")
    status = models.CharField(max_length=20, choices=STATUSES)
    note = models.CharField(max_length=300, blank=True)
    by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ["-created_at"]
