from selectable.base import ModelLookup
from selectable.registry import registry, LookupAlreadyRegistered

from models import Department, Institution

class DepartmentLookup(ModelLookup):
  
  model = Department
  search_fields = ('name__icontains',)

class InstitutionLookup(ModelLookup):
  
  model = Institution
  search_fields = ('name__icontains',)

for lookup in [DepartmentLookup, InstitutionLookup]:
  try:
    registry.register(lookup)
  except LookupAlreadyRegistered:
    pass
