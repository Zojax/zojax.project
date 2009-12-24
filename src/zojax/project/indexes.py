##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

$Id$
"""
from zojax.catalog.utils import Indexable
from zc.catalog.catalogindex import SetIndex, ValueIndex

from interfaces import ITask, IState, IDueDate, ITaskAttributes


def dateIndex():
    return ValueIndex('date', IDueDate)


def stateIndex():
    return ValueIndex('state', IState)


def taskCategoryIndex():
    return SetIndex('category', ITaskAttributes)


def taskMilestoneIndex():
    return ValueIndex('milestone', ITask)
