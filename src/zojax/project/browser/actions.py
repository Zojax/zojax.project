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
from zojax.members.browser.join import JoinAction
from zojax.content.draft.interfaces import IDraftedContent
from zojax.project.interfaces import _, ITask, IMilestone, IProject, ITasks

from interfaces import \
    IAddTaskAction, IAddMilestoneAction, IUploadAttachmentsAction


class AddTask(Action):
    interface.implements(IAddTaskAction)
    component.adapts(IMilestone, interface.Interface)

    weight = 5
    title = _(u'Add Task')
    contextInterface = IProject

    @property
    def url(self):
        return '%s/tasks/+/project.task/'%absoluteURL(self.context,self.request)

    def isAvailable(self):
        return (not IDraftedContent.providedBy(self.context)) and \
             ((checkPermission('zojax.AddTask', self.context) or
                checkPermission('zojax.SubmitTask', self.context)) and \
                'tasks' in self.context)


class AddMilestone(Action):
    interface.implements(IAddMilestoneAction)
    component.adapts(IMilestone, interface.Interface)

    weight = 6
    title = _(u'Add Milestone')
    contextInterface = IProject

    @property
    def url(self):
        return '%s/milestones/+/project.milestone/'%absoluteURL(
            self.context, self.request)

    def isAvailable(self):
        return (not IDraftedContent.providedBy(self.context)) and \
               checkPermission('zojax.AddMilestone', self.context) and \
            'milestones' in self.context


class UploadAttachmentsAction(Action):
    component.adapts(ITask, interface.Interface)
    interface.implements(IUploadAttachmentsAction)

    weight = 5
    title = _(u'Upload files')
    permission = 'zojax.AddContentAttachment'

    @property
    def url(self):
        return '%s/upload.html'%absoluteURL(self.context, self.request)


class JoinAction(JoinAction):

    title = _('Join this project')
