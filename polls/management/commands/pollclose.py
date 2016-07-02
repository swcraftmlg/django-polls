from django.core.management.base import BaseCommand, CommandError
from ...exceptions import QuestionError
from ...models import Question as Poll


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        for poll_id in options['poll_id']:
            try:
                poll = Poll.objects.get(pk=poll_id)
                poll.close()
            except Poll.DoesNotExist:
                raise CommandError('Poll "%s" does not exist' % poll_id)
            except QuestionError as e:
                raise CommandError(str(e))

            self.stdout.write(self.style.SUCCESS('Successfully closed poll "%s"' % poll_id))
