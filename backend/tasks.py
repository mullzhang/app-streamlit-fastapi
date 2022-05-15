import time

from celery import Celery

# Ref.
# https://riptutorial.com/celery/example/23628/celery-plus-redis
# https://djangobrothers.com/blogs/python_celery_local/

BROKER_URL = "redis://localhost:6379/0"
BACKEND_URL = "redis://localhost:6379/1"
app = Celery("tasks", broker=BROKER_URL, backend=BACKEND_URL)


@app.task
def add(x, y):
    return x + y


@app.task
def f():
    print("f関数開始")
    time.sleep(5)
    print("f関数終了")

    return {"result": {"message": "THIS IS A RESULT!"}}
