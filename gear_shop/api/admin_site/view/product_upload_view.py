from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
import pandas as pd
import io

from api.forms.excel_upload_form import ProductExcelUploadForm
from api.services.product_import_service import ProductImportService


@method_decorator(staff_member_required, name='dispatch')
class ProductExcelUploadView(View):
    template_name = 'admin/product_excel_upload.html'

    def get(self, request):
        form = ProductExcelUploadForm()
        return render(request, self.template_name, {
            'form': form,
            'title': 'Upload sản phẩm từ Excel',
            'opts': {'app_label': 'api', 'model_name': 'product'}
        })

    def post(self, request):
        form = ProductExcelUploadForm(request.POST, request.FILES)

        if form.is_valid():
            excel_file = form.cleaned_data['excel_file']

            # Import sản phẩm
            result = ProductImportService.import_products_from_excel(excel_file)

            if result['success']:
                if result['success_count'] > 0:
                    messages.success(
                        request,
                        f'Đã import thành công {result["success_count"]} sản phẩm!'
                    )

                if result['error_count'] > 0:
                    error_message = f'Có {result["error_count"]} lỗi xảy ra:\n' + '\n'.join(result['errors'])
                    messages.warning(request, error_message)

                return redirect('admin:api_product_changelist')
            else:
                messages.error(request, f'Lỗi import: {result["error"]}')

        return render(request, self.template_name, {
            'form': form,
            'title': 'Upload sản phẩm từ Excel',
            'opts': {'app_label': 'api', 'model_name': 'product'}
        })

@staff_member_required
def download_product_template(request):
    """Download file Excel mẫu với dropdown và formatting đẹp mắt"""

    try:
        # Tạo workbook với template nâng cao
        wb = ProductImportService.create_advanced_excel_template()

        # Tạo file Excel trong memory
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        # Tạo response
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="product_template_advanced.xlsx"'

        return response

    except Exception as e:
        # Fallback về template đơn giản nếu có lỗi
        sample_data = ProductImportService.get_sample_excel_data()
        df = pd.DataFrame(sample_data)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Products', index=False)

            # Thêm sheet hướng dẫn
            instructions = pd.DataFrame({
                'Cột': [
                    'name', 'category', 'brand', 'original_price', 'description',
                    'product_group', 'version', 'box_content', 'is_new', 'specifications'
                ],
                'Bắt buộc': [
                    'Có', 'Có', 'Không', 'Có', 'Không',
                    'Không', 'Không', 'Không', 'Không', 'Không'
                ],
                'Mô tả': [
                    'Tên sản phẩm',
                    'Tên danh mục (phải tồn tại trong hệ thống)',
                    'Tên thương hiệu (sẽ tự tạo nếu chưa có)',
                    'Giá gốc (số)',
                    'Mô tả sản phẩm (JSON hoặc text)',
                    'Nhóm sản phẩm',
                    'Phiên bản sản phẩm',
                    'Nội dung hộp (JSON hoặc text)',
                    'Sản phẩm mới (True/False)',
                    'Thông số kỹ thuật (JSON)'
                ]
            })
            instructions.to_excel(writer, sheet_name='Hướng dẫn', index=False)

        output.seek(0)
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="product_template.xlsx"'

        return response
