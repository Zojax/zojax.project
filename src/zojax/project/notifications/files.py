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


class TaskAttachmentsTemplate(TaskNotification):

    def update(self):
        super(TaskAttachmentsTemplate, self).update()

        attachs = self.context0
        self.comment = attachs.comment
        self.attachs = attachs.attachments

    @property
    def subject(self):
        return u'%s: Files uploaded to "%s"'%(
            self.project.title, self.context.title)
