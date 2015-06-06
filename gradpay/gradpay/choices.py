"""
Choices for survey model fields.
"""

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

CAREER_CHOICES = (
    ('academic', 'Academia / Education'),
    ('government', 'Government'),
    ('private', 'Private Sector'),
    ('nonprofit', 'Not-for-profit / NGO'),
    ('other', 'Other'),
)

SATISFACTION_CHOICES = (
    ('5', 'Very satisfied'),
    ('4', 'Somewhat satisfied'),
    ('3', 'Neither satisfied nor dissatisfied'),
    ('2', 'Somewhat dissatisfied'),
    ('1', 'Very dissatisfied'),
    ('NA', 'Not applicable: No support or benefits')
)
