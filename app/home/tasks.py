from celery import shared_task

@shared_task  # an example shared task
def test_shared_task():
    print('test_shared_task has run.')
    return