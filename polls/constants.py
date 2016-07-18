from django.conf import settings


PAGE_SIZE = settings.PAGE_SIZE

# Minimum amount of hours that a question must remain active
QUESTION_MIN_ACTIVE_HOURS = 24

# Maximum amount of votes for a question for a time span (per user)
CUOTA_VOTES_MAX_AMOUNT = 3
CUOTA_VOTES_TIMESPAN_HOURS = 1
