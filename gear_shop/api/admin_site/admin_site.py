from django.contrib.admin import AdminSite
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

class GearShopAdminSite(AdminSite):
    site_header = 'GearShop Admin Panel'
    site_title = 'GearShop Admin'
    index_title = 'Chào mừng đến với GearShop Admin'
    site_url = '/admin/'

    def each_context(self, request):
        """
        Return a dictionary of variables to put in the template context for
        *every* page in the admin site.
        """
        context = super().each_context(request)
        context.update({
            'site_header': self.site_header,
            'site_title': self.site_title,
            'index_title': self.index_title,
            'has_permission': request.user.is_active and request.user.is_staff,
        })
        return context

# Create custom admin site instance
admin_site = GearShopAdminSite(name='gearshop_admin')
