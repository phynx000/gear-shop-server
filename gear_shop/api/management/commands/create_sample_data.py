# management/commands/create_sample_data.py
from django.core.management.base import BaseCommand
from django.db import transaction

import random

from api.models import Product
from api.models.administrative import Province
from api.models.branch import Branch
from api.models.stock import Stock


class Command(BaseCommand):
    help = 'Create sample data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--products',
            type=int,
            default=10,
            help='Number of products to create'
        )
        parser.add_argument(
            '--branches',
            type=int,
            default=20,
            help='Number of branches to create'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # Tạo sản phẩm mẫu
        products_data = [
            'iPhone 15 Pro Max', 'Samsung Galaxy S24 Ultra', 'MacBook Air M3',
            'iPad Pro 12.9', 'AirPods Pro 2', 'Apple Watch Series 9',
            'Sony WH-1000XM5', 'Dell XPS 13', 'HP Pavilion 15',
            'Asus ROG Strix G15', 'Lenovo ThinkPad X1', 'Surface Pro 9'
        ]

        products = []
        for i, name in enumerate(products_data[:options['products']]):
            product = Product.objects.create(
                name=name,
                original_price=random.randint(500000, 50000000),
                description=f'Mô tả cho {name}'
            )
            products.append(product)

        self.stdout.write(f'Created {len(products)} products')

        # Lấy một số tỉnh và quận để tạo chi nhánh
        provinces = list(Province.objects.all()[:5])  # Lấy 5 tỉnh đầu

        if not provinces:
            self.stdout.write(
                self.style.WARNING('No provinces found. Please import administrative data first.')
            )
            return

        # Tạo chi nhánh mẫu
        branch_names = [
            'Chi nhánh Trung tâm', 'Chi nhánh Quận 1', 'Chi nhánh Quận 3',
            'Chi nhánh Quận 7', 'Chi nhánh Tân Bình', 'Chi nhánh Phú Nhuận',
            'Chi nhánh Gò Vấp', 'Chi nhánh Thủ Đức', 'Chi nhánh Bình Thạnh',
            'Chi nhánh Tân Phú', 'Chi nhánh Quận 2', 'Chi nhánh Quận 4',
            'Chi nhánh Quận 5', 'Chi nhánh Quận 6', 'Chi nhánh Quận 8',
            'Chi nhánh Quận 10', 'Chi nhánh Quận 11', 'Chi nhánh Quận 12',
            'Chi nhánh Hóc Môn', 'Chi nhánh Củ Chi'
        ]

        branches = []
        colors = ['Đỏ', 'Xanh', 'Đen', 'Trắng', 'Vàng', 'Hồng', 'Tím', 'Xám']

        for i, name in enumerate(branch_names[:options['branches']]):
            province = random.choice(provinces)
            districts = list(province.districts.all())

            if districts:
                district = random.choice(districts)
                wards = list(district.wards.all())
                ward = random.choice(wards) if wards else None
            else:
                district = None
                ward = None

            branch = Branch.objects.create(
                name=name,
                province=province,
                district=district,
                ward=ward,
                address=f'Số {random.randint(1, 999)} Đường {random.choice(["Nguyễn Huệ", "Lê Lợi", "Trần Hưng Đạo", "Hai Bà Trưng", "Điện Biên Phủ"])}',
                phone=f'028 {random.randint(1000, 9999)} {random.randint(1000, 9999)}'
            )
            branches.append(branch)

        self.stdout.write(f'Created {len(branches)} branches')

        # Tạo dữ liệu tồn kho
        stock_count = 0
        for product in products:
            # Mỗi sản phẩm có mặt tại 60-90% chi nhánh
            available_branches = random.sample(
                branches,
                random.randint(int(len(branches) * 0.6), int(len(branches) * 0.9))
            )

            for branch in available_branches:
                # Mỗi chi nhánh có 2-5 màu khác nhau
                available_colors = random.sample(
                    colors,
                    random.randint(2, min(5, len(colors)))
                )

                for color in available_colors:
                    quantity = random.randint(1, 50)
                    Stock.objects.create(
                        product=product,
                        branch=branch,
                        color=color,
                        quantity=quantity
                    )
                    stock_count += 1

        self.stdout.write(f'Created {stock_count} stock records')

        self.stdout.write(
            self.style.SUCCESS(
                f'Sample data created successfully!\n'
                f'- {len(products)} products\n'
                f'- {len(branches)} branches\n'
                f'- {stock_count} stock records'
            )
        )

# Để chạy các lệnh này, sử dụng:
# python manage.py import_administrative_data
# python manage.py create_sample_data