from django.core.management.base import BaseCommand
from api.models.products import Category, Brand
from django.db import transaction

class Command(BaseCommand):
    help = 'Sửa lỗi Unicode trong tên categories và brands'

    def handle(self, *args, **options):
        with transaction.atomic():
            # Mapping tên cũ -> tên mới (sử dụng tên chính xác từ database)
            category_fixes = {
                'Chuột my tnh': 'Chuột máy tính',
                'Bn Phm': 'Bàn phím',
                'Mn hnh': 'Màn hình',
            }

            self.stdout.write(self.style.SUCCESS('🔧 Bắt đầu sửa lỗi Unicode cho categories...'))

            fixed_count = 0
            for old_name, new_name in category_fixes.items():
                try:
                    category = Category.objects.get(name=old_name)
                    old_slug = category.slug
                    category.name = new_name
                    # Không cần update slug vì sẽ tự động tạo khi save
                    category.save()
                    fixed_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Đã sửa: "{old_name}" → "{new_name}"')
                    )
                except Category.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'⚠ Không tìm thấy category: "{old_name}"')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Lỗi khi sửa "{old_name}": {e}')
                    )

            # Hiển thị kết quả
            self.stdout.write(
                self.style.SUCCESS(f'\n📊 Đã sửa {fixed_count} categories. Danh sách sau khi sửa:')
            )
            for cat in Category.objects.all().order_by('name'):
                self.stdout.write(f'- {cat.name}')

            self.stdout.write(
                self.style.SUCCESS('\n🎉 Hoàn thành! Bây giờ có thể import Excel với tên chính xác.')
            )
