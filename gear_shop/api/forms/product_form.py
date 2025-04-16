from django import forms
from ..models.products import Product,Brand

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            "name": forms.TextInput(attrs={"size": 60}),  # Ô nhập name lớn hơn
            "description": forms.Textarea(attrs={"rows": 8, "cols": 100}),  # Ô nhập mô tả rộng hơn
        }

