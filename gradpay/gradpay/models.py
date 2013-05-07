# Django imports
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

import datetime
from django.utils.timezone import now

import settings
import activation

# Form choices

GENDER_CHOICES = (
    ('FM', 'Female'),
    ('ML', 'Male'),
    ('NS', 'Other'),
)

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

FEES_CHOICES = (
    ('YS', 'Yes'),
    ('NO', 'No'),
    ('NS', 'Not sure'),
)

CONTRACT_CHOICES = (
    ('YR', 'Each semester or year'),
    ('CT', 'Once at start of program (for entire program)'),
    ('NC', 'No contract'),
    ('NA', 'No support provided'),
    ('NS', 'Not sure'),
)

PART_TIME_CHOICES = (
    ('YS', 'Yes: Have or plan to work at a part-time job'),
    ('NO', 'No: Have not and do not plan to work at a part-time job'),
    ('NS', 'Not sure')
)

LOAN_CHOICES = (
    ('YS', 'Yes: Have or plan to take loans'),
    ('NO', 'No: Have not and do not plan to take loans'),
    ('NS', 'Not sure'),
)

UNION_CHOICES = (
    ('YS', 'Yes'),
    ('NO', 'No'),
    ('NS', 'Not sure'),
)

LEAVE_CHOICES = (
    ('PL', 'Yes: Paid medical/family leave'),
    ('UL', 'Yes: Unpaid medical/family leave'),
    ('NO', 'No medical/family leave'),
    ('NS', 'Not sure'),
)

SATISFACTION_CHOICES = (
    ('5', 'Very satisfied'),
    ('4', 'Somewhat satisfied'),
    ('3', 'Neither satisfied nor dissatisfied'),
    ('2', 'Somewhat dissatisfied'),
    ('1', 'Very dissatisfied'),
    ('NA', 'Not applicable: No support or benefits')
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

    county = models.CharField(max_length=256)
    county_code = models.CharField(max_length=5)
    state_code = models.CharField(max_length=2)

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

class SurveyManager(models.Manager):
    
    def delete_expired_surveys(self):
        
        for survey in self.all():
            if not survey.is_active:
                delta = datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
                if (survey.time_created + delta) < now():
                    survey.delete()

    def send_reminders(self):
        
        for survey in self.\
                filter(is_active=False).\
                exclude(activation_key='ACTIVATED'):
            activation.send_activation_email(survey)

class Survey(models.Model):
    
    # Timestamps
    time_modified = models.DateTimeField(auto_now=True)
    time_created = models.DateTimeField(auto_now_add=True)
    
    # Activation fields
    is_active = models.BooleanField(editable=False)
    activation_key = models.CharField(max_length=40, editable=False)
    
    # Email address
    email = models.EmailField(max_length=70, verbose_name='Email address', help_text='Note: You must use an academic [.edu] email address.')

    # Program
    institution = models.ForeignKey(Institution)
    department = models.ForeignKey(Department, help_text='Choose the best available option. Be as specific as possible.')
    degree = models.ManyToManyField(Degree, help_text='Which degree(s) are you pursuing? Check all that apply.')
    start_year = models.IntegerField(help_text='Year you began your program [yyyy].')
    graduation_year = models.IntegerField(help_text='Year of (expected) graduation [yyyy].')
    gender = models.CharField(max_length=16, choices=GENDER_CHOICES, blank=True, help_text='Which gender do you identify with?')
    age = models.PositiveIntegerField(blank=True, help_text='What is your age? Please enter a whole number.')
    international_student = models.CharField(max_length=16, choices=INTERNATIONAL_CHOICES, help_text='Are you an international student?')

    # Current year support
    stipend = models.PositiveIntegerField(verbose_name='<strong>Yearly</strong> stipend', help_text='Please enter your <strong>yearly</strong> pre-tax stipend or salary in US dollars, including any summer stipend. If you are paid in a different currency, please <a href="http://finance.yahoo.com/currency-converter/#to=USD" target="_blank">convert your stipend</a> to US dollars.')
    support_types = models.ManyToManyField(Support, blank=True, help_text='Which of the following funds your stipend or tuition, if any? Choose all that apply.')
    summer_stipend = models.CharField(max_length=16, choices=SUMMER_STIPEND_CHOICES, help_text='Do you receive a summer stipend?')
    tuition_coverage = models.CharField(max_length=16, choices=TUITION_CHOICES, help_text='Are your tuition fees covered?')
    tuition_amount = models.PositiveIntegerField(help_text='How much do you pay in tuition (not including tuition covered by your program)?', default=0)
    fees = models.CharField(max_length=16, choices=FEES_CHOICES, help_text='Are you required to pay any fees for your program (course fees, lab fees, etc.)?')
    fees_amount = models.PositiveIntegerField(help_text='How much do you pay in fees (not including fees covered by your program)?', default=0)

    # General support
    total_terms = models.PositiveIntegerField(help_text='Total number of terms you expect to be enrolled in your program.', validators=[MinValueValidator(1)])
    teaching_terms = models.PositiveIntegerField(help_text='Total number of terms you expect to work as a teaching assistant or instructor.')
    _teaching_fraction = models.FloatField(blank=False, editable=False)
    contract = models.CharField(max_length=16, choices=CONTRACT_CHOICES, help_text='If you have a contract, funding plan, or other agreement describing your support, how often is it negotiated?')
    part_time_work = models.CharField(max_length=16, choices=PART_TIME_CHOICES, verbose_name='Part-time work', help_text='Have you or do you plan to work at a part-time job during your graduate program (not including teaching or research assistantships)?')
    student_loans = models.CharField(max_length=16, choices=LOAN_CHOICES, help_text='Have you or do you plan to take out student loans <strong>during your graduate program</strong>? Do not include loans taken out before graduate school.')
    union_member = models.CharField(max_length=16, choices=UNION_CHOICES, help_text='Are you represented by a union?')
    
    # Benefits
    health_benefits = models.CharField(max_length=16, choices=BENEFIT_CHOICES, help_text='Does your program provide health benefits?')
    dental_benefits = models.CharField(max_length=16, choices=BENEFIT_CHOICES, help_text='Does your program provide dental benefits?')
    vision_benefits = models.CharField(max_length=16, choices=BENEFIT_CHOICES, help_text='Does your program provide vision benefits?')
    leave = models.CharField(max_length=16, choices=LEAVE_CHOICES, verbose_name='Family/medical leave', help_text='Are you eligible for family and/or medical leave (e.g., leave for illness, a family member\'s illness, or childbirth)?')

    # Summary
    satisfaction = models.CharField(max_length=16, choices=SATISFACTION_CHOICES, help_text='How satisfied are you with your financial support and benefits?', blank=False, default='...')
    comments = models.TextField(blank=True, help_text='Enter any comments about your financial support and benefits here.')

    objects = SurveyManager()

    def save(self):
        
        self._teaching_fraction = self.teaching_terms / float(self.total_terms)
        super(Survey, self).save()
