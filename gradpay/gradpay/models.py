# Django imports
from django import forms
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

def add_not_sure(choices):
  return choices + (('NS', 'Not sure'),)

# Form options
DEGREE_CHOICES = (
  ('MR', 'MA/MS only'),
  ('PHD', 'PhD only'),
  ('MRPHD', 'MA/MS and PhD'),
  ('OTH', 'Other'),
)

BENEFIT_CHOICES = (
  ('NO', 'Not provided'),
  ('YES', 'Provided for a fee'),
  ('PAY', 'Provided at no fee'),
  ('NS', 'Not sure'),
)

SALARY_MISC_CHOICES = (
  ('NO', 'No funding available'),
  ('GT', 'Can apply for funding'),
  ('PT', 'Partial funding provided'),
  ('FL', 'Full funding provided'),
  ('NS', 'Not sure'),
)

CONTRACT_CHOICES = (
  ('YR', 'Re-negotiated every year'),
  ('CT', 'Negotiated at start of program'),
  ('NA', 'No support provided'),
  ('NS', 'Not sure'),
)

LOAN_CHOICES = (
  ('YS', 'Yes'),
  ('NO', 'No'),
  ('NS', 'Not sure'),
)

SATISFACTION_CHOICES = (
  ('1', 'Very dissatisfied'),
  ('2', 'Somewhat dissatisfied'),
  ('3', 'Neither satisfied nor dissatisfied'),
  ('4', 'Somewhat satisfied'),
  ('5', 'Very satisfied'),
)

class Discipline(models.Model):
  """
  Field of study.
  """
  
  name = models.CharField(max_length=256)

  def __unicode__(self):
    return self.name

class Institution(models.Model):
  """
  Degree-granting instutition.
  """
  
  name = models.CharField(max_length=256)
  city = models.CharField(max_length=256)
  state = models.CharField(max_length=256)
  category = models.CharField(max_length=256)

  def __unicode__(self):
    return self.name

class Support(models.Model):
  """
  Source of financial support.
  """
  
  name = models.CharField(max_length=64)
  tooltip = models.CharField(max_length=256)

  def __unicode__(self):
    return self.name

class Survey(models.Model):
  
  # User
  user = models.ForeignKey(User, editable=False)

  # Timestamps
  time_modified = models.DateTimeField(auto_now=True)
  time_created = models.DateTimeField(auto_now_add=True)

  # Program
  institution = models.ForeignKey(Institution)
  department = models.ForeignKey(Discipline)
  #institution = models.CharField(max_length=256)
  #department = models.CharField(max_length=256)
  area = models.CharField(max_length=256, blank=True)
  degree = models.CharField(max_length=16, choices=DEGREE_CHOICES)
  start_year = models.IntegerField(verbose_name='Start year', help_text='Year you began your program [yyyy].')
  stop_year = models.IntegerField(verbose_name='Graduation year', help_text='Year of (expected) graduation [yyyy].')

  # Salary
  salary = models.PositiveIntegerField(help_text='Please enter your <strong>annual</strong> salary in $US.')
  salary_types = models.ManyToManyField(Support, help_text='How is your stipend paid? Choose all that apply.')
  contract = models.CharField(max_length=16, choices=CONTRACT_CHOICES)
  summer_funding = models.CharField(max_length=16, choices=SALARY_MISC_CHOICES, help_text='Does your program provide summer funding?')
  tuition = models.CharField(max_length=16, choices=SALARY_MISC_CHOICES, help_text='Does your program pay your tuition?')
  student_loans = models.CharField(max_length=16, choices=LOAN_CHOICES, help_text='Have you or do you plan to take out student loans during your program?')
  
  # Benefits
  health_benefits = models.CharField(max_length=16, choices=BENEFIT_CHOICES, help_text='Does your program provide health benefits?')
  dental_benefits = models.CharField(max_length=16, choices=BENEFIT_CHOICES, help_text='Does your program provide dental benefits?')
  vision_benefits = models.CharField(max_length=16, choices=BENEFIT_CHOICES, help_text='Does your program provide vision benefits?')

  satisfaction = models.CharField(max_length=16, choices=SATISFACTION_CHOICES, help_text='How satisfied are you with your funding?', blank=False, default='Unspecified')

  # Comments
  comments = models.TextField(blank=True)
