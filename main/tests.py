from django.test import TestCase
''' to use models without django run
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'ui_cli.settings'
import django
django.setup()
'''

'''
import asyncio
import time



async def slow_operation(future):
    await asyncio.sleep(1)
    future.set_result('Future is done!')

def got_result(future):
    print(future.result())
    loop.stop()

loop = asyncio.get_event_loop()
future = asyncio.Future()
asyncio.ensure_future(slow_operation(future))
future.add_done_callback(got_result)
try:
    loop.run_forever()
finally:
    loop.close()
'''


class Test():
    def __call__(self, arg):
        print('called with {}'.format(arg))

    def somefunc(self, arg):
        self(arg)


a = Test()

a.somefunc(3)

from asgiref.sync import async_to_sync, sync_to_async
import django_rq
from main.tasks import create

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'ui_cli.settings'
import django
django.setup()
from main.models import Server
print(Server.objects.get(pk=1))
#django_rq.enqueue(create)