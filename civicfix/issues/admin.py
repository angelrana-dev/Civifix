from django.contrib import admin
from .models import Department, Profile, Issue, StatusUpdate
admin.site.register([Department, Profile, StatusUpdate])
@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category", "status", "department", "reporter", "created_at")
    list_filter = ("status", "category", "department")
