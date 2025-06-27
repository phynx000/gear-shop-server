import pandas as pd
import json
from django.db import transaction
from ..models.products import Product, Category, Brand
from ..models.specification import Specification
from django.core.exceptions import ValidationError
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
import io

class ProductImportService:

    @staticmethod
    # def import_products_from_excel(excel_file):
    #     """
    #     Import sản phẩm từ file Excel
    #
    #     Expected columns:
    #     - name (bắt buộc): Tên sản phẩm
    #     - category (bắt buộc): Tên danh mục
    #     - original_price (bắt buộc): Giá gốc
    #     - brand (tùy chọn): Tên thương hiệu
    #     - description (tùy chọn): Mô tả sản phẩm (JSON string hoặc text)
    #     - product_group (tùy chọn): Nhóm sản phẩm
    #     - version (tùy chọn): Phiên bản
    #     - box_content (tùy chọn): Nội dung hộp (JSON string hoặc text)
    #     - is_new (tùy chọn): Sản phẩm mới (True/False)
    #     - specifications (tùy chọn): Thông số kỹ thuật (JSON string)
    #     """
    #
    #     try:
    #         # ĐỌC TỪ DÒNG 3 - bỏ qua header (dòng 1) và description (dòng 2)
    #         df = pd.read_excel(excel_file, skiprows=2)
    #
    #         print(f"🔍 DEBUG: Sau khi skip 2 dòng, còn {len(df)} dòng")
    #
    #         # In 3 dòng đầu để debug
    #         for i in range(min(3, len(df))):
    #             print(f"🔍 DEBUG Dòng {i+1}: {list(df.iloc[i])}")
    #
    #         # Loại bỏ các dòng trống hoàn toàn
    #         df = df.dropna(how='all')
    #         print(f"🔍 DEBUG: Sau khi drop dòng trống, còn {len(df)} dòng")
    #
    #         # Đổi tên cột để khớp với expected columns
    #         df.columns = [
    #             'name', 'category', 'brand', 'original_price', 'description',
    #             'product_group', 'version', 'box_content', 'is_new', 'specifications'
    #         ]
    #
    #         success_count = 0
    #         error_list = []
    #
    #         with transaction.atomic():
    #             for index, row in df.iterrows():
    #                 try:
    #                     row_num = index + 3  # +3 vì Excel bắt đầu từ 1, có 2 dòng header/description
    #
    #                     # Bỏ qua dòng trống hoàn toàn
    #                     if (pd.isna(row['name']) and pd.isna(row['category']) and
    #                         pd.isna(row['original_price']) and pd.isna(row['brand'])):
    #                         continue
    #
    #                     print(f"🔍 DEBUG: Xử lý dòng dữ liệu thực {row_num}")
    #
    #                     # Kiểm tra các trường bắt buộc
    #                     if pd.isna(row['name']) or str(row['name']).strip() == '':
    #                         error_list.append(f"Dòng {row_num}: Tên sản phẩm không được để trống")
    #                         continue
    #
    #                     if pd.isna(row['category']) or str(row['category']).strip() == '':
    #                         error_list.append(f"Dòng {row_num}: Danh mục không được để trống")
    #                         continue
    #
    #                     if pd.isna(row['original_price']) or str(row['original_price']).strip() == '':
    #                         error_list.append(f"Dòng {row_num}: Giá sản phẩm không được để trống")
    #                         continue
    #
    #                     # Validate và parse giá
    #                     try:
    #                         price = float(row['original_price'])
    #                         if price <= 0:
    #                             error_list.append(f"Dòng {row_num}: Giá sản phẩm phải lớn hơn 0")
    #                             continue
    #                     except (ValueError, TypeError):
    #                         error_list.append(f"Dòng {row_num}: Giá sản phẩm không hợp lệ")
    #                         continue
    #
    #                     # Lấy hoặc tạo category
    #                     category_name = str(row['category']).strip()
    #                     try:
    #                         category = Category.objects.get(name=category_name)
    #                     except Category.DoesNotExist:
    #                         error_list.append(f"Dòng {row_num}: Danh mục \"{category_name}\" không tồn tại")
    #                         continue
    #
    #                     # Lấy hoặc tạo brand nếu có
    #                     brand = None
    #                     if not pd.isna(row['brand']) and str(row['brand']).strip() != '':
    #                         brand_name = str(row['brand']).strip()
    #                         try:
    #                             brand = Brand.objects.get(name=brand_name)
    #                         except Brand.DoesNotExist:
    #                             error_list.append(f"Dòng {row_num}: Thương hiệu \"{brand_name}\" không tồn tại")
    #                             continue
    #
    #                     # Xử lý description
    #                     description = {}
    #                     if 'description' in df.columns and not pd.isna(row['description']):
    #                         desc_value = str(row['description']).strip()
    #                         try:
    #                             # Thử parse JSON
    #                             description = json.loads(desc_value)
    #                         except:
    #                             # Nếu không phải JSON, lưu dạng text
    #                             description = {"content": desc_value}
    #
    #                     # Xử lý box_content
    #                     box_content = {}
    #                     if 'box_content' in df.columns and not pd.isna(row['box_content']):
    #                         box_value = str(row['box_content']).strip()
    #                         try:
    #                             # Thử parse JSON
    #                             box_content = json.loads(box_value)
    #                         except:
    #                             # Nếu không phải JSON, lưu dạng text
    #                             box_content = {"content": box_value}
    #
    #                     # Xử lý is_new
    #                     is_new = False
    #                     if 'is_new' in df.columns and not pd.isna(row['is_new']):
    #                         is_new_value = str(row['is_new']).strip().lower()
    #                         is_new = is_new_value in ['true', '1', 'yes', 'có', 'đúng']
    #
    #                     # Tạo sản phẩm
    #                     product = Product.objects.create(
    #                         name=str(row['name']).strip(),
    #                         category=category,
    #                         brand=brand,
    #                         original_price=float(row['original_price']),
    #                         description=description,
    #                         product_group=str(row.get('product_group', '')).strip() or None,
    #                         version=str(row.get('version', '')).strip() or None,
    #                         box_content=box_content,
    #                         is_new=is_new
    #                     )
    #
    #                     # Thêm specifications nếu có
    #                     if 'specifications' in df.columns and not pd.isna(row['specifications']):
    #                         try:
    #                             specs_data = json.loads(str(row['specifications']))
    #                             if isinstance(specs_data, dict):
    #                                 for spec_name, spec_value in specs_data.items():
    #                                     Specification.objects.create(
    #                                         product=product,
    #                                         key=spec_name,  # Sửa từ 'name' thành 'key'
    #                                         value=str(spec_value)
    #                                     )
    #                             elif isinstance(specs_data, list):
    #                                 for spec in specs_data:
    #                                     if isinstance(spec, dict) and 'key' in spec and 'value' in spec:  # Sửa từ 'name' thành 'key'
    #                                         Specification.objects.create(
    #                                             product=product,
    #                                             key=spec['key'],  # Sửa từ 'name' thành 'key'
    #                                             value=spec['value']
    #                                         )
    #                         except json.JSONDecodeError:
    #                             # Nếu không phải JSON, bỏ qua specifications
    #                             pass
    #
    #                     success_count += 1
    #
    #                 except Exception as e:
    #                     error_list.append(f"Dòng {row_num}: {str(e)}")
    #                     continue
    #
    #         return {
    #             'success': True,
    #             'success_count': success_count,
    #             'error_count': len(error_list),
    #             'errors': error_list
    #         }
    #
    #     except Exception as e:
    #         return {
    #             'success': False,
    #             'error': str(e)
    #         }

    @staticmethod
    def import_products_from_excel(excel_file):
        """
        Import sản phẩm từ file Excel

        Expected columns:
        - name (bắt buộc): Tên sản phẩm
        - category (bắt buộc): Tên danh mục
        - original_price (bắt buộc): Giá gốc
        - brand (tùy chọn): Tên thương hiệu
        - description (tùy chọn): Mô tả sản phẩm (JSON string hoặc text)
        - product_group (tùy chọn): Nhóm sản phẩm
        - version (tùy chọn): Phiên bản
        - box_content (tùy chọn): Nội dung hộp (JSON string hoặc text)
        - is_new (tùy chọn): Sản phẩm mới (True/False)
        - specifications (tùy chọn): Thông số kỹ thuật (JSON string)
        """
        try:
            # Đọc file Excel từ header trở đi (không skip dòng nào)
            df = pd.read_excel(excel_file)

            print(f"🔍 DEBUG: Đọc được {len(df)} dòng từ file Excel")
            print(f"🔍 DEBUG: Columns: {list(df.columns)}")

            # Kiểm tra nếu file trống
            if len(df) == 0:
                return {
                    'success': False,
                    'error': 'File Excel không có dữ liệu'
                }

            # In 3 dòng đầu để debug
            for i in range(min(3, len(df))):
                print(f"🔍 DEBUG Dòng {i+1}: {list(df.iloc[i])}")

            # Kiểm tra nếu dòng đầu tiên có chứa text mô tả thì bỏ qua
            # if len(df) > 0:
            #     first_row = df.iloc[0]
            #     if any(str(cell).upper().find('BẮT BUỘC') != -1 or str(cell).upper().find('TÙY CHỌN') != -1 for cell in first_row):
            #         print("🧹 Đã phát hiện và loại bỏ dòng mô tả đầu tiên")
            #         df = df.iloc[1:]

            # Loại bỏ các dòng trống hoàn toàn
            df = df.dropna(how='all')
            print(f"🔍 DEBUG: Sau khi clean, còn {len(df)} dòng")

            # Kiểm tra nếu không còn dữ liệu nào
            if len(df) == 0:
                return {
                    'success': False,
                    'error': 'File Excel không có dữ liệu hợp lệ sau khi loại bỏ dòng trống'
                }

            # Đổi tên cột để khớp với expected columns
            expected_columns = [
                'name', 'category', 'brand', 'original_price', 'description',
                'product_group', 'version', 'box_content', 'is_new', 'specifications'
            ]

            # Đảm bảo có đủ số cột
            while len(df.columns) < len(expected_columns):
                df[f'empty_col_{len(df.columns)}'] = None

            df.columns = expected_columns[:len(df.columns)]

            success_count = 0
            error_list = []

            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        row_num = index + 2  # Excel thực tế (tính từ dòng header)

                        # Bỏ qua dòng trống hoàn toàn
                        if (pd.isna(row['name']) and pd.isna(row['category']) and
                                pd.isna(row['original_price']) and pd.isna(row['brand'])):
                            continue

                        print(f"🔍 DEBUG: Xử lý dòng {row_num}")

                        # Kiểm tra các trường bắt buộc
                        if pd.isna(row['name']) or str(row['name']).strip() == '':
                            error_list.append(f"Dòng {row_num}: Tên sản phẩm không được để trống")
                            continue

                        if pd.isna(row['category']) or str(row['category']).strip() == '':
                            error_list.append(f"Dòng {row_num}: Danh mục không được để trống")
                            continue

                        if pd.isna(row['original_price']) or str(row['original_price']).strip() == '':
                            error_list.append(f"Dòng {row_num}: Giá sản phẩm không được để trống")
                            continue

                        # Validate và parse giá
                        try:
                            price = float(row['original_price'])
                            if price <= 0:
                                error_list.append(f"Dòng {row_num}: Giá sản phẩm phải lớn hơn 0")
                                continue
                        except (ValueError, TypeError):
                            error_list.append(f"Dòng {row_num}: Giá sản phẩm không hợp lệ")
                            continue

                        # Lấy hoặc tạo category
                        category_name = str(row['category']).strip()
                        try:
                            category = Category.objects.get(name=category_name)
                        except Category.DoesNotExist:
                            error_list.append(f"Dòng {row_num}: Danh mục \"{category_name}\" không tồn tại")
                            continue

                        # Lấy hoặc tạo brand nếu có
                        brand = None
                        if not pd.isna(row['brand']) and str(row['brand']).strip() != '':
                            brand_name = str(row['brand']).strip()
                            try:
                                brand = Brand.objects.get(name=brand_name)
                            except Brand.DoesNotExist:
                                error_list.append(f"Dòng {row_num}: Thương hiệu \"{brand_name}\" không tồn tại")
                                continue

                        # Xử lý description
                        description = {}
                        if 'description' in df.columns and not pd.isna(row['description']):
                            desc_value = str(row['description']).strip()
                            try:
                                # Thử parse JSON
                                description = json.loads(desc_value)
                            except:
                                # Nếu không phải JSON, lưu dạng text
                                description = {"content": desc_value}

                        # Xử lý box_content
                        box_content = {}
                        if 'box_content' in df.columns and not pd.isna(row['box_content']):
                            box_value = str(row['box_content']).strip()
                            try:
                                # Thử parse JSON
                                box_content = json.loads(box_value)
                            except:
                                # Nếu không phải JSON, lưu dạng text
                                box_content = {"content": box_value}

                        # Xử lý is_new
                        is_new = False
                        if 'is_new' in df.columns and not pd.isna(row['is_new']):
                            is_new_value = str(row['is_new']).strip().lower()
                            is_new = is_new_value in ['true', '1', 'yes', 'có', 'đúng']

                        # Tạo sản phẩm
                        product = Product.objects.create(
                            name=str(row['name']).strip(),
                            category=category,
                            brand=brand,
                            original_price=price,
                            description=description,
                            product_group=str(row.get('product_group', '')).strip() or None,
                            version=str(row.get('version', '')).strip() or None,
                            box_content=box_content,
                            is_new=is_new
                        )

                        # Thêm specifications nếu có
                        if 'specifications' in df.columns and not pd.isna(row['specifications']):
                            try:
                                specs_data = json.loads(str(row['specifications']))
                                if isinstance(specs_data, dict):
                                    for spec_name, spec_value in specs_data.items():
                                        Specification.objects.create(
                                            product=product,
                                            key=spec_name,
                                            value=str(spec_value)
                                        )
                                elif isinstance(specs_data, list):
                                    for spec in specs_data:
                                        if isinstance(spec, dict) and 'key' in spec and 'value' in spec:
                                            Specification.objects.create(
                                                product=product,
                                                key=spec['key'],
                                                value=spec['value']
                                            )
                            except json.JSONDecodeError:
                                pass

                        success_count += 1

                    except Exception as e:
                        error_list.append(f"Dòng {row_num}: {str(e)}")
                        continue

            return {
                'success': True,
                'success_count': success_count,
                'error_count': len(error_list),
                'errors': error_list
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def create_advanced_excel_template():
        """Tạo file Excel template với dropdown và formatting đẹp mắt"""

        # Tạo workbook mới
        wb = Workbook()
        ws = wb.active
        ws.title = "Nhập sản phẩm"

        # Lấy dữ liệu thật từ database
        categories = list(Category.objects.all().values_list('name', flat=True).order_by('name'))
        brands = list(Brand.objects.all().values_list('name', flat=True).order_by('name'))

        # In thông tin để debug
        print(f"📊 Loaded {len(categories)} categories: {categories[:5]}..." if categories else "⚠ No categories found")
        print(f"📊 Loaded {len(brands)} brands: {brands[:5]}..." if brands else "⚠ No brands found")

        # Định nghĩa headers
        headers = [
            'name', 'category', 'brand', 'original_price', 'description',
            'product_group', 'version', 'box_content', 'is_new', 'specifications'
        ]

        # Định nghĩa màu sắc và style
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True, size=12)

        # Border style
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

        # Tạo header row (chỉ 1 dòng)
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border

        # Thêm dữ liệu mẫu (bắt đầu từ dòng 2) - SỬ DỤNG TÊN CATEGORIES CÓ SẴN TRONG DATABASE
        sample_data = [
            [
                'Chuột Gaming Logitech G502 HERO',
                'Chuột máy tính',  # Sử dụng tên có sẵn trong DB
                'Logitech',
                1590000,
                'Chuột gaming cao cấp với cảm biến HERO 25K',
                'Gaming Mouse',
                'Phiên bản mới 2024',
                'Chuột, Cáp USB, Hướng dẫn sử dụng',
                'Có',
                '{"DPI": "25600", "Kết nối": "USB", "Trọng lượng": "121g", "LED": "RGB"}'
            ],
            [
                'Bàn phím cơ Corsair K70 RGB MK.2',
                'Bàn phím',  # Sử dụng tên có sẵn trong DB
                'Corsair',
                2890000,
                'Bàn phím cơ gaming với switch Cherry MX',
                'Mechanical Keyboard',
                'Cherry MX Red',
                'Bàn phím, Keycap puller, Hướng dẫn',
                'Không',
                '{"Switch": "Cherry MX Red", "Backlight": "RGB", "Layout": "Full-size", "Kết nối": "USB-C"}'
            ],
            [
                'Tai nghe SteelSeries Arctis 7P',
                'Tai nghe',  # Tên này đã đúng trong DB
                'SteelSeries',
                3200000,
                'Tai nghe gaming không dây cao cấp',
                'Gaming Headset',
                'Wireless',
                'Tai nghe, USB receiver, Cáp sạc, Micro rời',
                'Có',
                '{"Kết nối": "2.4GHz Wireless", "Pin": "24 giờ", "Driver": "40mm", "Micro": "Có thể tháo rời"}'
            ]
        ]

        # Thêm dữ liệu mẫu vào sheet (bắt đầu từ dòng 2)
        for row_num, row_data in enumerate(sample_data, 2):
            for col_num, value in enumerate(row_data, 1):
                cell = ws.cell(row=row_num, column=col_num, value=value)
                cell.border = thin_border
                if col_num in [4]:  # Cột giá
                    cell.number_format = '#,##0'

        # Tạo dropdown cho category (cột B)
        if categories:
            category_validation = DataValidation(
                type="list",
                formula1=f'"{",".join(categories)}"',
                allow_blank=True
            )
            category_validation.error = 'Vui lòng chọn danh mục từ danh sách'
            category_validation.errorTitle = 'Lỗi nhập liệu'
            ws.add_data_validation(category_validation)
            category_validation.add(f'B5:B1000')  # Áp dụng từ dòng 5 đến 1000

        # Tạo dropdown cho brand (cột C)
        if brands:
            brand_validation = DataValidation(
                type="list",
                formula1=f'"{",".join(brands)}"',
                allow_blank=True
            )
            brand_validation.error = 'Vui lòng chọn thương hiệu từ danh sách hoặc nhập thương hiệu mới'
            brand_validation.errorTitle = 'Lỗi nhập liệu'
            ws.add_data_validation(brand_validation)
            brand_validation.add(f'C5:C1000')

        # Tạo dropdown cho is_new (cột I)
        new_validation = DataValidation(
            type="list",
            formula1='"Có,Không"',
            allow_blank=True
        )
        new_validation.error = 'Vui lòng chọn "Có" hoặc "Không"'
        new_validation.errorTitle = 'Lỗi nhập liệu'
        ws.add_data_validation(new_validation)
        new_validation.add(f'I5:I1000')

        # Điều chỉnh độ rộng cột
        column_widths = {
            'A': 35,  # name
            'B': 20,  # category
            'C': 15,  # brand
            'D': 12,  # price
            'E': 40,  # description
            'F': 20,  # product_group
            'G': 15,  # version
            'H': 40,  # box_content
            'I': 12,  # is_new
            'J': 50   # specifications
        }

        for col, width in column_widths.items():
            ws.column_dimensions[col].width = width

        # Đóng băng hàng đầu
        ws.freeze_panes = 'A3'

        # Tạo sheet hướng dẫn
        guide_ws = wb.create_sheet("Hướng dẫn")

        # Nội dung hướng dẫn
        guide_content = [
            ["HƯỚNG DẪN SỬ DỤNG FILE EXCEL NHẬP SẢN PHẨM", ""],
            ["", ""],
            ["1. CÁC CỘT BẮT BUỘC:", ""],
            ["   • name: Tên sản phẩm", ""],
            ["   • category: Danh mục (chọn từ dropdown)", ""],
            ["   • original_price: Giá gốc (chỉ nhập số)", ""],
            ["", ""],
            ["2. CÁC CỘT TÙY CHỌN:", ""],
            ["   • brand: Thương hiệu (chọn từ dropdown hoặc nhập mới)", ""],
            ["   • description: Mô tả sản phẩm", ""],
            ["   • product_group: Nhóm sản phẩm", ""],
            ["   • version: Phiên bản", ""],
            ["   • box_content: Nội dung hộp", ""],
            ["   • is_new: Sản phẩm mới (chọn Có/Không)", ""],
            ["   • specifications: Thông số kỹ thuật (format JSON)", ""],
            ["", ""],
            ["3. VÍ DỤ SPECIFICATIONS:", ""],
            ['   {"DPI": "25600", "Kết nối": "USB", "LED": "RGB"}', ""],
            ["", ""],
            ["4. LƯU Ý:", ""],
            ["   • Không được để trống các cột bắt buộc", ""],
            ["   • Giá chỉ nhập số, không có ký tự đặc biệt", ""],
            ["   • Specifications phải đúng format JSON", ""],
            ["   • Danh mục phải tồn tại trong hệ thống", ""],
        ]

        # Thêm nội dung hướng dẫn
        for row_num, (col1, col2) in enumerate(guide_content, 1):
            guide_ws.cell(row=row_num, column=1, value=col1)
            guide_ws.cell(row=row_num, column=2, value=col2)

            # Styling cho tiêu đề
            if row_num == 1:
                cell = guide_ws.cell(row=row_num, column=1)
                cell.font = Font(bold=True, size=14, color="4472C4")
                cell.alignment = Alignment(horizontal="center")

        # Điều chỉnh độ rộng cột cho sheet hướng dẫn
        guide_ws.column_dimensions['A'].width = 60
        guide_ws.column_dimensions['B'].width = 30

        # Trả về workbook
        return wb

    @staticmethod
    def get_sample_excel_data():
        """Trả về dữ liệu mẫu đơn giản (deprecated - sử dụng create_advanced_excel_template thay thế)"""
        return [
            {
                'name': 'iPhone 15 Pro Max',
                'category': 'Smartphone',
                'brand': 'Apple',
                'original_price': 29990000,
                'description': '{"content": "iPhone mới nhất của Apple"}',
                'product_group': 'iPhone 15 Series',
                'version': '256GB',
                'box_content': '{"items": ["Máy", "Cáp sạc", "Tài liệu"]}',
                'is_new': 'True',
                'specifications': '{"Màn hình": "6.7 inch", "RAM": "8GB", "Chip": "A17 Pro"}'
            },
            {
                'name': 'Samsung Galaxy S24 Ultra',
                'category': 'Smartphone',
                'brand': 'Samsung',
                'original_price': 26990000,
                'description': '{"content": "Flagship mới nhất của Samsung"}',
                'product_group': 'Galaxy S24 Series',
                'version': '512GB',
                'box_content': '{"items": ["Máy", "Cáp sạc", "S Pen", "Tài liệu"]}',
                'is_new': 'True',
                'specifications': '{"Màn hình": "6.8 inch", "RAM": "12GB", "Chip": "Snapdragon 8 Gen 3"}'
            }
        ]
