# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger(__name__)
LOCKFILE = "/tmp/queue_runner.lock"
RUN_LIMIT = 60


def run():
    """
    Spusti chroustace fronty.
    """
    import os
    import sys

    # nejede uz nejaky runner?
    try:
        lockfile = os.open(LOCKFILE, os.O_CREAT | os.O_EXCL)
    except OSError:
        print >> sys.stderr, "Lockfile exists (%s). Aborting." % LOCKFILE
        sys.exit(1)

    # podme ogari na to!
    try:
        run_queue()
    except:
        pass
    finally:
        # pryc s lockfile
        os.close(lockfile)
        os.unlink(LOCKFILE)


def run_queue():
    """
    Chroustac fronty -- foukne do fronty task a spusti jej.
    """
    import ipdb; ipdb.set_trace()

    from hazard.shared.director import director
    if director.current:
        logger.info('Run: current buffer is full')
        return

    # vytahneme task z fronty
    from hazard.geo.forms import KMLForm

    while director.is_queued():
        for task in director.queue:
            # yes! vyzobneme data
            data = dict(zip(
                ['hells', 'buildings', 'email', 'ip'],
                director.queue[task].split('\n')
            ))
            ip = data.pop('ip', '')

            # zpracujeme je
            form = KMLForm(data=data, ip=ip)
            if form.is_valid():
                form.save(ip)
            else:
                import ipdb; ipdb.set_trace()
                logger.warn('Run: processing of task %s was not successfull' % task)

            # ukoncime aktualni task
            director.done(task)

    # kanec
    logger.info('Run: no task to run')


def watcher():
    """
    Sleduje ukoly v current bufferu a loguje dobu jejich cinnosti.
    """
    import time
    from hazard.shared.director import director

    now = time.time()
    for k in director.current.keys():
        score = director.get_task_score(k)
        diff = now + score
        msg = 'Task %s run for %i seconds' % (k, diff)
        level = logging.DEBUG if diff < RUN_LIMIT else logging.WARN
        logger.log(level, msg)
