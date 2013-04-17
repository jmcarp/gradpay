'''Add FIPS codes for state and county to each institition.'''

# Django imports
from django.core.management.base import NoArgsCommand

# Project imports
from gradpay.models import Institution
from gradpay.geo import geocode

class Command(NoArgsCommand):

    help = 'Add FIPS codes'
    
    def handle_noargs(self, **options):
        
        for inst in Institution.objects.all():

            # Get state info
            if inst.state_code is None:
                inst.state_code = geocode.f.state_to_code(inst.state)

            # Get county info
            if True:#inst.county is None or inst.county_code is None:
                inst.county, inst.county_code = geocode.geocode_institution(
                    inst.name,
                    inst.city,
                    inst.state
                )
                print inst.name, inst.city, inst.state, inst.county
            
            # Save changes
            inst.save()
