import random
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from issues.models import Department, Profile, Issue, StatusUpdate, DEPT_FOR

class Command(BaseCommand):
    help = "Create departments, demo users and sample issues"
    def handle(self, *a, **kw):
        depts = {n: Department.objects.get_or_create(name=n)[0] for n in DEPT_FOR.values()}
        def mk(name, role, dept=None, **extra):
            u, new = User.objects.get_or_create(username=name, defaults=extra)
            if new: u.set_password("demo1234")
            if not u.email: u.email = f"{name}@example.com"
            u.save()
            Profile.objects.get_or_create(user=u, defaults={"role": role, "department": dept})
            return u
        mk("admin1", "admin", is_staff=True, is_superuser=True)
        for n in depts.values(): mk("officer_" + n.name.split()[0].lower(), "officer", n)
        cit = mk("citizen1", "citizen")
        if not Issue.objects.exists():
            samples = [("Overflowing bins near market", "garbage", "Bins have not been cleared for three days."),
                       ("Streetlight out on main road", "streetlight", "The whole stretch is dark after 7 pm."),
                       ("Large pothole near school gate", "road", "Two-wheelers are swerving to avoid it."),
                       ("Pipe leaking at junction", "water", "Water has been flowing onto the road since morning.")]
            for t, c, d in samples:
                i = Issue.objects.create(title=t, category=c, description=d, reporter=cit, address="Sample address",
                                         latitude=20.5937 + random.uniform(-.02, .02), longitude=78.9629 + random.uniform(-.02, .02))
                StatusUpdate.objects.create(issue=i, status="assigned", by=cit, note=f"Reported and routed to {i.department}")
        self.stdout.write(self.style.SUCCESS("Demo ready. Password for all demo users: demo1234"))