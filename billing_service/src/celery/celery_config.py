from datetime import timedelta

from celery import Celery

app = Celery('subscription_renewal', broker='redis://localhost:6379/0')
app.control.purge()
app.autodiscover_tasks(['src.celery.tasks'])

app.conf.beat_schedule = {
    'subscription-renewal-every-hour': {
        'task': 'src.celery.tasks.subscription_renewal',
        'schedule': timedelta(hours=1),  # Every 10 seconds
    },
}
app.conf.timezone = 'UTC'
