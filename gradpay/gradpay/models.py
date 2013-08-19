# Django imports
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

import datetime
from django.utils.timezone import now

import choices
import settings
import activation

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
    gender = models.CharField(
        max_length=16, 
        choices=choices.GENDER_CHOICES, 
        help_text='[Optional] Which gender do you identify with?',
        blank=True
    )
    age = models.PositiveIntegerField(
        help_text='[Optional] What is your age? Please enter a whole number.',
        blank=True
    )
    international_student = models.CharField(
        max_length=16, 
        choices=choices.INTERNATIONAL_CHOICES, 
        help_text='Are you an international student?'
    )
    linkedin = models.CharField(
        max_length=256, 
        verbose_name='LinkedIn Profile URL', 
        help_text='''
            [Optional] Please enter the URL of your LinkedIn public profile.
            Not sure what your URL is? Click <a href="/linkedinfo/" target="_blank">here</a> for help.
            <span id="linkedin_helper">Or click here to detect your public URL automatically:</span>
            <br />
            <script type="IN/login" data-onAuth="onAuth"></script>
        ''',
        blank=True
    )

    # Current year support
    stipend = models.PositiveIntegerField(
        verbose_name='<strong>Yearly</strong> stipend', 
        help_text='''Please enter your <strong>yearly</strong> pre-tax 
            stipend or salary in US dollars, including any summer stipend. 
            If you are paid in a different currency, please 
            <a href="http://finance.yahoo.com/currency-converter/#to=USD" 
            target="_blank">convert your stipend</a> to US dollars.'''
    )
    support_types = models.ManyToManyField(
        Support, 
        blank=True, 
        help_text='''Which of the following funds your stipend or 
            tuition, if any? Choose all that apply.'''
    )
    summer_stipend = models.CharField(
        max_length=16, 
        choices=choices.SUMMER_STIPEND_CHOICES, 
        help_text='Do you receive a summer stipend?'
    )
    tuition_coverage = models.CharField(
        max_length=16, 
        choices=choices.TUITION_CHOICES, 
        help_text='Are your tuition fees covered?'
    )
    tuition_amount = models.PositiveIntegerField(
        default=0,
        help_text='''How much do you pay in tuition (not including 
            tuition covered by your program)?'''
    )
    fees = models.CharField(
        max_length=16, 
        choices=choices.FEES_CHOICES, 
        help_text='''Are you required to pay any fees for your 
            program (course fees, lab fees, etc.)?'''
    )
    fees_amount = models.PositiveIntegerField(
        default=0,
        help_text='''How much do you pay in fees (not including 
            fees covered by your program)?'''
    )

    # General support
    total_terms = models.PositiveIntegerField(
        help_text='Total number of terms you expect to be enrolled in your program.', 
        validators=[MinValueValidator(1)]
    )
    teaching_terms = models.PositiveIntegerField(
        help_text='Total number of terms you expect to work as a teaching assistant or instructor.'
    )
    _teaching_fraction = models.FloatField(
        blank=False, 
        editable=False
    )
    contract = models.CharField(
        max_length=16, 
        choices=choices.CONTRACT_CHOICES, 
        help_text='''If you have a contract, funding plan, or other 
            agreement describing your support, how often is it negotiated?'''
    )
    part_time_work = models.CharField(
        max_length=16, 
        choices=choices.PART_TIME_CHOICES, 
        verbose_name='Part-time work', 
        help_text='''Have you or do you plan to work at a part-time job 
            during your graduate program (not including teaching or 
            research assistantships)?'''
    )
    student_loans = models.CharField(
        max_length=16, 
        choices=choices.LOAN_CHOICES, 
        help_text='''Have you or do you plan to take out student loans 
            <strong>during your graduate program</strong>? Do not include 
            loans taken out before graduate school.'''
    )
    _has_student_loans = models.IntegerField(
        blank=False, 
        editable=False
    )
    _has_part_time_work = models.IntegerField(
        blank=False,
        editable=False
    )
    _has_fellowship = models.IntegerField(
        blank=False,
        editable=False
    )
    union_member = models.CharField(
        max_length=16, 
        choices=choices.UNION_CHOICES, 
        help_text='Are you represented by a union?'
    )
    _is_union_member = models.IntegerField(
        blank=False,
        editable=False
    )
    
    # Benefits
    health_benefits = models.CharField(
        max_length=16, 
        choices=choices.BENEFIT_CHOICES, 
        help_text='Does your program provide health benefits?'
    )

    dental_benefits = models.CharField(
        max_length=16, 
        choices=choices.BENEFIT_CHOICES, 
        help_text='Does your program provide dental benefits?'
    )

    vision_benefits = models.CharField(
        max_length=16, 
        choices=choices.BENEFIT_CHOICES, 
        help_text='Does your program provide vision benefits?'
    )

    leave = models.CharField(
        max_length=16, 
        choices=choices.LEAVE_CHOICES, 
        verbose_name='Family/medical leave', 
        help_text='Are you eligible for family and/or medical leave (e.g., leave for illness, a family member\'s illness, or childbirth)?'
    )

    # Summary
    satisfaction = models.CharField(
        max_length=16, 
        choices=choices.SATISFACTION_CHOICES, 
        help_text='How satisfied are you with your financial support and benefits?', 
        blank=False, 
        default='...'
    )

    career = models.CharField(
        max_length=16,
        help_text='Which of the following best describes your desired career after you complete your program?',
        verbose_name='Career plans',
        choices=choices.CAREER_CHOICES
    )

    comments = models.TextField(
        blank=True, 
        help_text='Enter any comments about your financial support and benefits here.'
    )

    objects = SurveyManager()

    def save(self):
        """ Update auto-generated fields. """

        self._teaching_fraction = self.teaching_terms / float(self.total_terms)
        self._has_student_loans = int(self.student_loans == 'YS')
        self._has_part_time_work = int(self.part_time_work == 'YS')
        self._is_union_member = int(self.union_member == 'YS')

        fellowship = Support.objects.get(name='Competitive grant/fellowship to student')
        self._has_fellowship = int(fellowship in self.support_types.all())

        super(Survey, self).save()
