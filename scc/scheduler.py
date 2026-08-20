#!/usr/bin/env python3
"""
SC-Controller - Scheduler

Centralized scheduler that should be used everywhere.
Runs in SCCDaemon's (single-threaded) mainloop. That means all callbacks are
also called on main thread.

Use schedule(delay, callback, *data) to register one-time task.
"""
import time
import queue
import logging

log = logging.getLogger("Scheduler")


class Scheduler(object):
    def __init__(self):
        self._scheduled = queue.PriorityQueue()
        self._next = None
        self._now = time.time()

    def schedule(self, delay, callback, *data):
        """
        Schedules one-time task to be executed no sooner than after 'delay' of
        seconds. Delay may be float number.
        'callback' is called as callback(*data).
        """
        task = Task(self, self._now + delay, callback, data)
        self._scheduled.put(task)
        self._next = None
        return task

    def run(self):
        self._now = time.time()
        while not self._scheduled.empty():
            task = self._scheduled.queue[0]
            if task.cancelled or task.when > self._now:
                break
            self._scheduled.get()
            self._next = None
            if not task.cancelled:
                task.callback(*task.data)

    def get_next(self):
        while not self._scheduled.empty():
            task = self._scheduled.queue[0]
            if task.cancelled:
                self._scheduled.get()
                continue
            return task.when
        return None


class Task(object):
    def __init__(self, scheduler, when, callback, data):
        self.scheduler = scheduler
        self.when = when
        self.callback = callback
        self.data = data
        self.cancelled = False

    def cancel(self):
        self.cancelled = True

    def __lt__(self, other):
        return self.when < other.when
