# management/commands/import_administrative_data.py
from django.core.management.base import BaseCommand
from django.db import transaction
import requests
import json

from api.models.administrative import Province, District, Ward


class Command(BaseCommand):
    help = 'Import administrative data for Vietnam provinces, districts, and wards'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            type=str,
            default='api',
            choices=['api', 'json'],
            help='Data source: api (from online API) or json (from local file)'
        )
        parser.add_argument(
            '--file',
            type=str,
            help='Path to JSON file if using json source'
        )

    def handle(self, *args, **options):
        source = options['source']

        if source == 'api':
            self.import_from_api()
        else:
            file_path = options.get('file')
            if not file_path:
                self.stdout.write(
                    self.style.ERROR('Please provide --file argument when using json source')
                )
                return
            self.import_from_json(file_path)

    def import_from_api(self):
        """Import dữ liệu từ API online"""
        self.stdout.write('Importing administrative data from API...')

        # API endpoint để lấy dữ liệu hành chính Việt Nam
        api_url = "https://provinces.open-api.vn/api/?depth=3"

        try:
            response = requests.get(api_url, timeout=30)
            response.raise_for_status()
            data = response.json()

            self.process_data(data)

        except requests.RequestException as e:
            self.stdout.write(
                self.style.ERROR(f'Error fetching data from API: {e}')
            )
            return

    def import_from_json(self, file_path):
        """Import dữ liệu từ file JSON"""
        self.stdout.write(f'Importing administrative data from {file_path}...')

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.process_data(data)

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'File not found: {file_path}')
            )
            return
        except json.JSONDecodeError as e:
            self.stdout.write(
                self.style.ERROR(f'Invalid JSON file: {e}')
            )
            return

    @transaction.atomic
    def process_data(self, data):
        """Xử lý và import dữ liệu vào database"""

        # Đếm số lượng
        province_count = 0
        district_count = 0
        ward_count = 0

        for province_data in data:
            # Tạo tỉnh/thành
            province, created = Province.objects.get_or_create(
                code=province_data['code'],
                defaults={
                    'name': province_data['name'],
                    'type': province_data.get('type', 'Tỉnh')
                }
            )

            if created:
                province_count += 1
                self.stdout.write(f'Created province: {province.name}')

            # Xử lý quận/huyện
            for district_data in province_data.get('districts', []):
                district, created = District.objects.get_or_create(
                    code=district_data['code'],
                    defaults={
                        'name': district_data['name'],
                        'type': district_data.get('type', 'Huyện'),
                        'province': province
                    }
                )

                if created:
                    district_count += 1

                # Xử lý phường/xã
                for ward_data in district_data.get('wards', []):
                    ward, created = Ward.objects.get_or_create(
                        code=ward_data['code'],
                        defaults={
                            'name': ward_data['name'],
                            'type': ward_data.get('type', 'Xã'),
                            'district': district
                        }
                    )

                    if created:
                        ward_count += 1

        # Hiển thị kết quả
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully imported:\n'
                f'- {province_count} provinces\n'
                f'- {district_count} districts\n'
                f'- {ward_count} wards'
            )
        )


