from selectable.base import ModelLookup
from selectable.registry import registry, LookupAlreadyRegistered

from models import Discipline, Institution

class DisciplineLookup(ModelLookup):
  
  model = Discipline
  search_fields = ('name__icontains',)

class InstitutionLookup(ModelLookup):
  
  model = Institution
  search_fields = ('name__icontains',)

for lookup in [DisciplineLookup, InstitutionLookup]:
  try:
    registry.register(lookup)
  except LookupAlreadyRegistered:
    pass
