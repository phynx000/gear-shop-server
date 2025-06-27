from django.core.management.base import BaseCommand
from api.models.products import Category

class Command(BaseCommand):
    help = 'Hiển thị chi tiết tên categories để debug Unicode'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('📋 Chi tiết categories trong database:'))

        categories = Category.objects.all().order_by('id')
        for cat in categories:
            # Hiển thị tên với encoding details
            name_bytes = cat.name.encode('utf-8')
            self.stdout.write(
                f'ID: {cat.id} | Name: "{cat.name}" | Length: {len(cat.name)} | Bytes: {len(name_bytes)}'
            )

        self.stdout.write(
            self.style.WARNING('\n⚠ Nếu thấy tên bị thiếu dấu tiếng Việt, đó là lỗi Unicode!')
        )
