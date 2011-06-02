# -*- coding: utf-8 -*-

import time
import redis
import logging

from django.conf import settings
from django.utils.datastructures import SortedDict

QKEY = 'queue'
PREFIX = 'k_'
logger = logging.getLogger(__name__)


class Director(object):
    """
    Kdo je tady reditel? http://www.csfd.cz/film/222772-kdo-je-tady-reditel/

    Jednoduchy task manazer, s pomoci ktereho resime "synchronizaci" behem
    pridavani novych a aktualizaci starych map.
    """

    def __init__(self):
        if 'redis' in settings.CACHES['default']['BACKEND']:
            host, port = settings.CACHES['default']['LOCATION'].split(':')
            db = settings.CACHES['default']['OPTIONS']['DB'] + 1
        else:
            host, port, db = 'localhost', 6379, 1
        logger.debug('Director redis DB=%i' % db)
        self.client = redis.Redis(host=host, port=int(port), db=db)

    def select_db(self, db):
        logger.debug('Director redis DB=%i' % db)
        self.client.select(db=db)

    def add(self, task, value=''):
        """
        Prida do fronty dalsi ukol. Pokud je mozne ukol hned zpracovat, vrati
        True.
        """
        if self.client.zscore(QKEY, task) is None:
            # task ve fronte chybi, zaradime jej tam
            score = self.get_score()
            pipe = self.client.pipeline()
            pipe.zadd(QKEY, task, score).set(PREFIX + task, value)
            pipe.execute()
            logger.debug('Task %s is not present in queue, lets add it with score %s and value %s' % (task, score, value))
            return score < 0
        logger.debug('Task %s is already in queue' % task)
        return False

    def get_score(self, force_current=False):
        score = time.time()
        if force_current or self.client.zcard(QKEY) == 0:
            score = -1 * score
        return score

    def get_task_score(self, task):
        return self.client.zscore(QKEY, task)

    def get_current(self):
        """
        Vrati seznam aktualne zpracovavanych tasku.
        """
        task = self.client.zrangebyscore(QKEY, '-Inf', 0)
        values = self.client.mget([PREFIX + i for i in task]) if task else []
        tasks = dict(zip(task, values))
        logger.debug('Current running tasks: %s' % tasks)
        return tasks
    current = property(get_current)

    def get_queue(self):
        """
        Vrati seznam tasku cekajicich na zpracovani.
        """
        task = self.client.zrangebyscore(QKEY, 0, '+Inf')
        values = self.client.mget([PREFIX + i for i in task]) if task else []
        tasks = SortedDict(zip(task, values))
        logger.debug('Waiting tasks: %s' % tasks)
        return tasks
    queue = property(get_queue)

    def done(self, task):
        """
        Dokonci zadany ukol (odstrani jej z fronty).
        """
        score = self.get_task_score(task)
        if score < 0:
            pipe = self.client.pipeline()
            pipe.zrem(QKEY, task).delete(PREFIX + task)
            results = pipe.execute()
            logger.debug('Task %s is done' % task)
            return reduce(lambda a, b: a or b, results)
        else:
            return False

    def next(self):
        """
        Vezme z fronty dalsi ukol a oznaci jej jakoze se na nem prave pracuje.
        """
        if self.current:
            logger.debug('It is not possible to append new task, because current queue is not empty')
            return False # na necem se zrovna dela, nemuzeme rozjizdet novou vec

        to_proceed = self.client.zrangebyscore(QKEY, 0, 'Inf', 0, 1)
        if not to_proceed:
            logger.debug('There is not any other task waiting for execution')
            return False # ve fronte nic neni

        score = self.get_score(True)
        self.client.zadd(QKEY, to_proceed[0], score)
        logger.debug('Next task %s was added to current queue' % to_proceed[0])
        return to_proceed[0]

    def done_and_next(self, task):
        """
        Dokonci zadany ukol a vezme z fronty dalsi.
        """
        self.done(task)
        return self.next()

    def is_waiting(self, task):
        score = self.get_task_score(task)
        return score > 0 and score is not None

    def is_queued(self):
        task = self.client.zrangebyscore(QKEY, 0, '+Inf')
        return len(task) > 0

director = Director()
