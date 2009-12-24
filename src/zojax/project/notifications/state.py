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
from templates import TaskNotification


class TaskStateTemplate(TaskNotification):

    def update(self):
        super(TaskStateTemplate, self).update()

        self.state = self.context0.state

    @property
    def subject(self):
        if self.state == 2:
            return u'%s: Task completed "%s"'%(
                self.project.title, self.context.title)
        else:
            return u'%s: Task re-opened "%s"'%(
                self.project.title, self.context.title)
