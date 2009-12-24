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
from zope.security import checkPermission
from zope.traversing.browser import absoluteURL
from zojax.content.actions.action import Action

from zojax.project.interfaces import _, ITask, IMilestone
from zojax.project.browser.interfaces import \
    ICompleteTaskAction, IReopenTaskAction


class CompleteTask(Action):
    component.adapts(ITask, interface.Interface)
    interface.implements(ICompleteTaskAction)

    weight = 5
    title = _(u'Complete')

    @property
    def url(self):
        return '%s/complete.html'%absoluteURL(self.context, self.request)

    def isAvailable(self):
        return self.context.state == 1 and \
            checkPermission('zojax.CompleteTask', self.context)


class ReopenTask(Action):
    component.adapts(ITask, interface.Interface)
    interface.implements(IReopenTaskAction)

    weight = 5
    title = _(u'Re-open')
    permission = 'zojax.ReopenTask'

    @property
    def url(self):
        return '%s/reopen.html'%absoluteURL(self.context, self.request)

    def isAvailable(self):
        return self.context.state == 2 and \
            checkPermission('zojax.ReopenTask', self.context)
