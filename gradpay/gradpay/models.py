# Django imports
from django.db import models
from django.contrib.auth.models import User

# Form choices

DEGREE_CHOICES = (
  ('MR', 'Master\'s (MA, MS, MSW, etc.)'),
  ('DC', 'Doctoral (PhD)'),
  ('MD', 'Medical Doctor (MD/DVM/DO)'),
)

INTERNATIONAL_CHOICES = (
  ('YS', 'Yes'),
  ('NO', 'No'),
)

BENEFIT_CHOICES = (
  ('NO', 'Not provided'),
  ('YES', 'Provided for a fee'),
  ('PAY', 'Provided at no fee'),
  ('NS', 'Not sure'),
)

SUMMER_STIPEND_CHOICES = (
  ('NO', 'No summer stipend available'),
  ('GT', 'Can apply for summer stipend'),
  ('PT', 'Partial summer stipend provided'),
  ('FL', 'Full summer stipend provided'),
  ('NS', 'Not sure'),
)

TUITION_CHOICES = (
  ('NO', 'No tuition support available'),
  ('GT', 'Can apply for tuition support'),
  ('PT', 'Partial tuition support provided'),
  ('FL', 'Full tuition support provided'),
  ('NA', 'Not applicable: No tuition costs'),
  ('NS', 'Not sure'),
)

CONTRACT_CHOICES = (
  ('YR', 'Each semester or year'),
  ('CT', 'Once at start of program (for entire program)'),
  ('NA', 'No contract / no support provided'),
  ('NS', 'Not sure'),
)

LOAN_CHOICES = (
  ('YS', 'Yes: Have taken or plan to take loans'),
  ('NO', 'No: Have not taken and do not plan to take loans'),
  ('NS', 'Not sure'),
)

SATISFACTION_CHOICES = (
  ('5', 'Very satisfied'),
  ('4', 'Somewhat satisfied'),
  ('3', 'Neither satisfied nor dissatisfied'),
  ('2', 'Somewhat dissatisfied'),
  ('1', 'Very dissatisfied'),
)

class Department(models.Model):
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

class Degree(models.Model):
  """
  Degree.
  """
  
  name = models.CharField(max_length=256)

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
  department = models.ForeignKey(Department, help_text='Choose the best available option. Be as specific as possible.')
  degree = models.ManyToManyField(Degree, help_text='Which degree(s) are you pursuing? Check all that apply.')
  start_year = models.IntegerField(help_text='Year you began your program [yyyy].')
  graduation_year = models.IntegerField(help_text='Year of (expected) graduation [yyyy].')
  international_student = models.CharField(max_length=16, choices=INTERNATIONAL_CHOICES, help_text='Are you an international student?')

  # Current year support
  stipend = models.PositiveIntegerField(help_text='Please enter your <strong>annual</strong> stipend or salary in US dollars. If you are paid in a different currency, please <a href="http://finance.yahoo.com/currency-converter/#to=USD" target="_blank">convert your stipend</a> to US dollars.')
  support_types = models.ManyToManyField(Support, blank=True, help_text='Which of the following funds your stipend or tuition, if any? Choose all that apply.')
  summer_stipend = models.CharField(max_length=16, choices=SUMMER_STIPEND_CHOICES, help_text='Do you receive a summer stipend?')
  tuition_coverage = models.CharField(max_length=16, choices=TUITION_CHOICES, help_text='Are your tuition fees covered?')

  # General support
  total_terms = models.IntegerField(help_text='Total number of terms you expect to be enrolled in your program.')
  teaching_terms = models.IntegerField(help_text='Number of terms you expect to work as a teaching assistant or instructor.')
  contract = models.CharField(max_length=16, choices=CONTRACT_CHOICES, help_text='If you have a contract, funding plan, or other agreement describing your support, how often is it negotiated?')
  student_loans = models.CharField(max_length=16, choices=LOAN_CHOICES, help_text='Have you or do you plan to take out student loans during your graduate program?')
  
  # Benefits
  health_benefits = models.CharField(max_length=16, choices=BENEFIT_CHOICES, help_text='Does your program provide health benefits?')
  dental_benefits = models.CharField(max_length=16, choices=BENEFIT_CHOICES, help_text='Does your program provide dental benefits?')
  vision_benefits = models.CharField(max_length=16, choices=BENEFIT_CHOICES, help_text='Does your program provide vision benefits?')

  # Summary
  satisfaction = models.CharField(max_length=16, choices=SATISFACTION_CHOICES, help_text='How satisfied are you with your support?', blank=False, default='...')
  comments = models.TextField(blank=True, help_text='Enter any comments about your support here.')
