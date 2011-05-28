
from models import *


class StationForm(ModelForm):
    class Meta:
        model = Station
    
    def __init__(self, *args, **kwds):
        super(StationForm, self).__init__(*args, **kwds)
        self.fields['organization'].queryset = Organization.objects.order_by('name')
        self.fields['department'].queryset = Department.objects.order_by('name')
        self.fields['conference'].queryset = Conference.objects.order_by('title')
        self.fields['session'].queryset = Session.objects.order_by('name')
        self.fields['professor'].queryset = Professor.objects.order_by('name')
        
        
