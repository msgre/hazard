# -*- coding: utf-8 -*-

"""
TODO:
RPOPLPUSH source destination

- nebudu nekde evidovat pocet requestu?
- nebo pocet rozbehlych workeru?
    - jako abych pripadne omezil spousteni novych pracantu, kdyby toho bylo moc...


zadd
"""

import redis

CURRENT = 'current'
QUEUE_LIST = 'queue_list'
QUEUE_SET = 'queue_set'


class Director(object):
    """
    TODO:
    """

    def __init__(self):
        self.client = redis.Redis(host='localhost', port=6379, db=1)

    def add(self, slug):
        """
        Zaradi slug ke zpracovani:
        * pokud je mozne slug zpracovat okamzite, foukne ho do current bufferu
          a vrati True
        * pokud to mozne neni, foukne ho do fronty a vrati False
        """
        if not self.client.scard(QUEUE_SET):
            # prave se na nicem nedela, zpracujeme slug hnedka
            pipe = self.client.pipeline()
            pipe.lpush(CURRENT, slug).sadd(QUEUE_SET, slug)
            pipe.execute()
            return True
        elif not self.client.sismember(QUEUE_SET, slug):
            # slug jeste neni ve fronte, foukneme ho tam
            pipe = self.client.pipeline()
            pipe.lpush(QUEUE_LIST, slug).sadd(QUEUE_SET, slug)
            pipe.execute()
        else:
            # slug uz ve fronte je, takze se driv nebo pozdeji zpracuje
            pass
        return False

    def done(self):
        """
        Vrati slug na kterem se prave dopracovalo a vyprazdni se current
        buffer. V opacnem pripade vraci False.
        """
        if not self.client.llen(CURRENT):
            return False
        slug = self.client.lpop(CURRENT)
        self.client.srem(QUEUE_SET, slug)
        return slug

    def next(self):
        """
        Vytahne z fronty dalsi slug ke zpracovani, foukne ho do current
        bufferu a vrati jej. Pokud neni mozne zaradit dalsi prvek do current
        bufferu (protoze se budto na necem prave dela, nebo je fronta prazdna),
        vrati False.
        """
        if self.client.llen(CURRENT) or not self.client.llen(QUEUE_LIST):
            # uz se na necem dela, nebo je fronta prazdna
            return False
        return self.client.rpoplpush(QUEUE_LIST, CURRENT)

    def current(self):
        """
        Vrati jmeno slugu, na kterem se prave pracuje.
        """
        return self.client.rpoplpush(CURRENT, CURRENT)


director = Director()


class Worker(object):

    def do_it_baby(self):
        """
        TODO:
        """
        slug = director.next()
        if not slug:
            return False
