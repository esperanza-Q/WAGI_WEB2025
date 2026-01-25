from django.core.management.base import BaseCommand
from recruit.models import Category


class Command(BaseCommand):
    help = "모집 게시판 카테고리 생성"

    def handle(self, *args, **options):
        category_names = ["동아리", "공모전", "스터디"]

        for name in category_names:
            category, created = Category.objects.get_or_create(
                category_name=name
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"카테고리 생성: {name}"))
            else:
                self.stdout.write(self.style.WARNING(f"이미 존재하는 카테고리: {name}"))