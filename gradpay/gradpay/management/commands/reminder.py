# Django imports
from django.core.management.base import NoArgsCommand

# Project imports
from gradpay.models import Survey

class Command(NoArgsCommand):

  help = 'Delete expired surveys'
  
  def handle_noargs(self, **options):
    Survey.objects.send_reminders()
