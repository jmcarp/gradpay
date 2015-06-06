import re
import functools

from selectable.base import ModelLookup
from selectable.registry import registry, LookupAlreadyRegistered

from models import Department, Institution


class FlexModelLookup(ModelLookup):

    sub_patterns = []

    def get_query(self, request, term):
        term = functools.reduce(
            lambda x, y: re.sub(y[0], y[1], x),
            self.sub_patterns,
            term,
        )
        term = self.join_pattern.join(term)
        return super(FlexModelLookup, self).get_query(request, term)


class DepartmentLookup(ModelLookup):

    model = Department
    search_fields = ('name__icontains',)


class InstitutionLookup(FlexModelLookup):

    model = Institution
    search_fields = ('name__iregex',)
    sub_patterns = [
        ['[\s\-,]', ''],
    ]
    join_pattern = '[\s\-,]*'


for lookup in [DepartmentLookup, InstitutionLookup]:
    try:
        registry.register(lookup)
    except LookupAlreadyRegistered:
        pass
