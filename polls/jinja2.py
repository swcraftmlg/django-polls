from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.urlresolvers import reverse

from jinja2 import Environment


def pluralize(number, singular='', plural='s'):
    return singular if number == 1 else plural


def environment(**options):
    env = Environment(**options)

    env.filters['max'] = max
    env.filters['min'] = min
    env.filters['pluralize'] = pluralize

    env.globals.update({
        'static': staticfiles_storage.url,
        'url': reverse,
    })

    return env
