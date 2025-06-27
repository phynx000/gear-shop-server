from django import forms
import pandas as pd
from django.core.exceptions import ValidationError
from ..models.products import Product, Category, Brand
import json

class ProductExcelUploadForm(forms.Form):
    excel_file = forms.FileField(
        label='File Excel sản phẩm',
        help_text='Chọn file Excel (.xlsx, .xls) chứa danh sách sản phẩm',
        widget=forms.FileInput(attrs={
            'accept': '.xlsx,.xls',
            'class': 'form-control'
        })
    )

    def clean_excel_file(self):
        file = self.cleaned_data['excel_file']

        # Kiểm tra định dạng file
        if not file.name.endswith(('.xlsx', '.xls')):
            raise ValidationError('Chỉ chấp nhận file Excel (.xlsx, .xls)')

        # Kiểm tra kích thước file (tối đa 5MB)
        if file.size > 5 * 1024 * 1024:
            raise ValidationError('File không được vượt quá 5MB')

        try:
            # Đọc file Excel
            df = pd.read_excel(file)

            # Kiểm tra các cột bắt buộc
            required_columns = ['name', 'category', 'original_price']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                raise ValidationError(f'File thiếu các cột bắt buộc: {", ".join(missing_columns)}')

            # Kiểm tra dữ liệu không được rỗng
            if df.empty:
                raise ValidationError('File Excel không có dữ liệu')

            # Validate từng dòng
            errors = []
            for index, row in df.iterrows():
                row_num = index + 2  # +2 vì Excel bắt đầu từ 1 và có header

                # Kiểm tra tên sản phẩm
                if pd.isna(row['name']) or str(row['name']).strip() == '':
                    errors.append(f'Dòng {row_num}: Tên sản phẩm không được để trống')

                # Kiểm tra category tồn tại
                if not pd.isna(row['category']):
                    try:
                        Category.objects.get(name=str(row['category']).strip())
                    except Category.DoesNotExist:
                        errors.append(f'Dòng {row_num}: Danh mục "{row["category"]}" không tồn tại')

                # Kiểm tra brand nếu có
                if 'brand' in df.columns and not pd.isna(row['brand']):
                    try:
                        Brand.objects.get(name=str(row['brand']).strip())
                    except Brand.DoesNotExist:
                        errors.append(f'Dòng {row_num}: Thương hiệu "{row["brand"]}" không tồn tại')

                # Kiểm tra giá
                if pd.isna(row['original_price']):
                    errors.append(f'Dòng {row_num}: Giá sản phẩm không được để trống')
                else:
                    try:
                        price = float(row['original_price'])
                        if price <= 0:
                            errors.append(f'Dòng {row_num}: Giá sản phẩm phải lớn hơn 0')
                    except (ValueError, TypeError):
                        errors.append(f'Dòng {row_num}: Giá sản phẩm không hợp lệ')

            if errors:
                raise ValidationError('\n'.join(errors))

        except pd.errors.EmptyDataError:
            raise ValidationError('File Excel rỗng hoặc không hợp lệ')
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise ValidationError(f'Lỗi đọc file Excel: {str(e)}')

        return file
