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
from zope import interface
from zojax.content.notifications.interfaces import IContentNotification
from zojax.project.interfaces import _


class ITasksNotification(IContentNotification):
    """ tasks notification """


class ITaskAttachments(interface.Interface):
    """ uploaded attachments list """

    comment  = interface.Attribute('Comment')
    attachments = interface.Attribute('List of task attachments')


class IAssigneeTasksNotification(IContentNotification):
    """ tasks notification by assignees """


class IMilestonesNotification(IContentNotification):
    """ milestones notification """


class ITaskMailView(interface.Interface):
    """ pagelet type """
