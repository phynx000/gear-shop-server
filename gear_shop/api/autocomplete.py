from dal import autocomplete
from .models.administrative import District, Ward

class DistrictAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return District.objects.none()

        qs = District.objects.all()

        province_id = self.forwarded.get('province')
        if province_id:
            qs = qs.filter(province_id=province_id)

        return qs

class WardAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Ward.objects.none()

        qs = Ward.objects.all()

        district_id = self.forwarded.get('district')
        if district_id:
            qs = qs.filter(district_id=district_id)

        return qs
