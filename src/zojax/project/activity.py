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
from zope import interface, component
from zope.component import getUtility

from zojax.activity.record import ActivityRecord
from zojax.activity.interfaces import IActivity, IActivityRecordDescription
from zojax.content.activity.interfaces import IContentActivityRecord

from interfaces import _, IState, IStateActivityRecord, IStateChangedEvent


class StateActivityRecord(ActivityRecord):
    interface.implements(IStateActivityRecord, IContentActivityRecord)

    score = 0.5
    type = u'task.state'

    @property
    def verb(self):
        if self.state == 1:
            return _('re-opened')
        else:
            return _('completed')


class StateActivityRecordDescription(object):
    interface.implements(IActivityRecordDescription)

    title = _(u'Task state')
    description = _(u'Task state has been changed.')


@component.adapter(IState, IStateChangedEvent)
def stateChangedHandler(object, event):
    getUtility(IActivity).add(
        object, StateActivityRecord(state=object.state))
