from django.core.management.base import BaseCommand
from api.models.products import Category, Brand
from django.db import IntegrityError

class Command(BaseCommand):
    help = 'Tạo dữ liệu mẫu cho Category và Brand để test import Excel'

    def get_default_categories_data(self):
        """Trả về dữ liệu categories mặc định nếu database trống"""
        return [
            {'name': 'Chuột máy tính', 'code': 'MOUSE_001'},
            {'name': 'Bàn phím', 'code': 'KEYBOARD_001'},
            {'name': 'Tai nghe', 'code': 'HEADSET_001'},
            {'name': 'Màn hình', 'code': 'MONITOR_001'},
            {'name': 'CPU', 'code': 'CPU_001'},
            {'name': 'RAM', 'code': 'RAM_001'},
            {'name': 'Ổ cứng', 'code': 'STORAGE_001'},
            {'name': 'VGA', 'code': 'VGA_001'},
            {'name': 'Mainboard', 'code': 'MOBO_001'},
            {'name': 'Nguồn máy tính', 'code': 'PSU_001'},
        ]

    def get_default_brands_data(self):
        """Trả về dữ liệu brands mặc định nếu database trống"""
        return [
            'Logitech', 'Corsair', 'SteelSeries', 'ASUS', 'Intel', 'Samsung',
            'NVIDIA', 'AMD', 'MSI', 'Gigabyte', 'Razer', 'HyperX',
            'Cooler Master', 'Thermaltake', 'EVGA', 'Seasonic', 'Western Digital',
            'Seagate', 'Kingston', 'G.Skill', 'Crucial', 'LG', 'AOC', 'Dell'
        ]

    def load_categories_from_db(self):
        """Load categories từ database, nếu trống thì sử dụng dữ liệu mặc định"""
        existing_categories = Category.objects.all()
        if existing_categories.exists():
            self.stdout.write(
                self.style.SUCCESS(f'📊 Tìm thấy {existing_categories.count()} danh mục trong database')
            )
            return [{'name': cat.name, 'code': cat.code} for cat in existing_categories]
        else:
            self.stdout.write(
                self.style.WARNING('⚠ Database trống, sử dụng dữ liệu mặc định cho categories')
            )
            return self.get_default_categories_data()

    def load_brands_from_db(self):
        """Load brands từ database, nếu trống thì sử dụng dữ liệu mặc định"""
        existing_brands = Brand.objects.all()
        if existing_brands.exists():
            self.stdout.write(
                self.style.SUCCESS(f'📊 Tìm thấy {existing_brands.count()} thương hiệu trong database')
            )
            return [brand.name for brand in existing_brands]
        else:
            self.stdout.write(
                self.style.WARNING('⚠ Database trống, sử dụng dữ liệu mặc định cho brands')
            )
            return self.get_default_brands_data()

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Bắt đầu tải dữ liệu categories và brands...')
        )

        # Load dữ liệu từ database hoặc sử dụng mặc định
        categories_data = self.load_categories_from_db()
        brands_data = self.load_brands_from_db()

        # Tạo categories
        created_categories = 0
        for cat_data in categories_data:
            try:
                category, created = Category.objects.get_or_create(
                    name=cat_data['name'],
                    defaults={'code': cat_data['code']}
                )
                if created:
                    created_categories += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Tạo danh mục: {category.name}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠ Danh mục đã tồn tại: {category.name}')
                    )
            except IntegrityError:
                # Xử lý trường hợp slug trùng lặp
                self.stdout.write(
                    self.style.WARNING(f'⚠ Danh mục "{cat_data["name"]}" có vấn đề với slug, bỏ qua.')
                )

        # Tạo brands
        created_brands = 0
        for brand_name in brands_data:
            try:
                brand, created = Brand.objects.get_or_create(name=brand_name)
                if created:
                    created_brands += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Tạo thương hiệu: {brand.name}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠ Thương hiệu đã tồn tại: {brand.name}')
                    )
            except IntegrityError:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Thương hiệu "{brand_name}" có vấn đề, bỏ qua.')
                )

        # Hiển thị thống kê dữ liệu hiện có
        total_categories = Category.objects.count()
        total_brands = Brand.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Hoàn thành! Đã tạo {created_categories} danh mục và {created_brands} thương hiệu mới.'
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'📊 Tổng số danh mục: {total_categories}, Tổng số thương hiệu: {total_brands}'
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                '\n📝 Bây giờ bạn có thể tải template Excel và import sản phẩm!'
            )
        )
