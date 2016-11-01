# -*- coding: utf-8 -*-
import os

import shutil

__author__ = 'ihe'

DOIT_CONFIG = {'default_tasks': ['build']}
app_name = 'graform'


def task_sdist():
    return {
        'actions': ['python setup.py sdist'],
        'task_dep': ['rename-logging'],
        'verbosity': 2
    }


def rename_logging():
    src = os.path.join('m3u_dump', 'logging-prod.conf')
    dst = os.path.join('m3u_dump', 'logging.conf')
    shutil.move(src, dst)
    print('moved {0} -> {1}'.format(src, dst))


def task_rename_logging():
    return {
        'basename': 'rename-logging',
        'actions': [rename_logging],
        'verbosity': 2
    }
