import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'minishop.settings')

# CreOate the Celery appD
app = Celery('minishop')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Configure the periodic tasks
app.conf.beat_schedule = {
    'update-tgju-gold-price-every-3-minutes': {
        'task': 'goldapi.goldapifun.update_gold_price',
        'schedule': 180.0,  # Every 3 minutes
        'kwargs': {'provider_name': 'tgju'},
    },
    # Add more scheduled tasks for different providers as needed
    # Example:
    # 'update-other-provider-gold-price-every-5-minutes': {
    #     'task': 'goldapi.goldapifun.update_gold_price',
    #     'schedule': 300.0,  # Every 5 minutes
    #     'kwargs': {'provider_name': 'other_provider'},
    # },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 