'''
Add MEDIAN aggregate. Code adapted from http://coder.cl/2011/09/custom-aggregates-on-django/
'''

from django.db import models
 
class MedianSQL(models.sql.aggregates.Aggregate):
  sql_function = 'MEDIAN'
 
class Median(models.Aggregate):
  name = 'Median'

  def add_to_query(self, query, alias, col, source, is_summary):
    aggregate = MedianSQL(col,
                          source=source,
                          is_summary=is_summary,
                          **self.extra)
    query.aggregates[alias] = aggregate
