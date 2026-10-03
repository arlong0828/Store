from django.core.management.base import BaseCommand, CommandError

from store_app.models import member


class Command(BaseCommand):
    help = "Rebuild local OpenCV embeddings from members' stored profile photos."

    def add_arguments(self, parser):
        parser.add_argument("--name", help="Only rebuild one member by name.")

    def handle(self, *args, **options):
        from store_app.services.local_face import enroll_member

        accounts = member.objects.all().order_by("id")
        if options["name"]:
            accounts = accounts.filter(cName=options["name"])
        if not accounts.exists():
            raise CommandError("找不到符合條件的會員。")

        failures = 0
        for account in accounts:
            try:
                enroll_member(account)
            except Exception as error:
                failures += 1
                self.stderr.write(self.style.ERROR(f"{account.cName}: {error}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"{account.cName}: 已建立本機人臉特徵"))

        if failures:
            raise CommandError(f"有 {failures} 位會員建立失敗。")
