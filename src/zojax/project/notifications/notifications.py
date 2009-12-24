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
from zope.component import getUtility, getAdapter
from zope.app.intid.interfaces import IIntIdAddedEvent
from zope.app.container.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from zojax.assignment.interfaces import IAssignments, IPrincipalAssignedEvent
from zojax.subscription.interfaces import ISubscriptionDescription
from zojax.content.type.interfaces import IDraftedContent
from zojax.content.notifications.utils import sendNotification
from zojax.content.notifications.notification import Notification
from zojax.project.interfaces import ITask, IProject, IMilestone, ITaskComment
from zojax.project.notifications.interfaces import \
    _, ITasksNotification, IAssigneeTasksNotification, IMilestonesNotification


class TasksNotification(Notification):
    component.adapts(ITask)
    interface.implementsOnly(ITasksNotification)

    type = u'tasks'
    title = _(u'Task notifications')
    description = _(u'All task notifications (add/edit/delete, comments, files upload, completed/re-open actions).')


class TasksNotificationDescription(object):
    interface.implements(ISubscriptionDescription)

    type = u'tasks'
    title = _(u'Task notifications')
    description = _(u'All task notifications (add/edit/delete, comments, files upload, completed/re-open actions).')


class AssigneeTasksNotification(Notification):
    component.adapts(ITask)
    interface.implementsOnly(IAssigneeTasksNotification)

    type = u'assigneetasks'
    title = _(u'Task notifications by assignee')
    description = _(u'Only assignee will receive notifications for add/edit/delete, comments, files upload, completed/re-open actions.')


class AssigneeTasksNotificationDescription(object):
    interface.implements(ISubscriptionDescription)

    type = u'assigneetasks'
    title = _(u'Task notifications by assignee')
    description = _(u'Only assignee will receive notifications for add/edit/delete, comments, files upload, completed/re-open actions.')


class MilestonesNotification(Notification):
    component.adapts(IMilestone)
    interface.implementsOnly(IMilestonesNotification)

    type = u'milestones'
    title = _(u'Milestone notifications')
    description = _(u'add, edit due date, completed/re-open actions.')


class MilestonesNotificationDescription(object):
    interface.implements(ISubscriptionDescription)

    type = u'milestones'
    title = _(u'Milestone notifications')
    description = _(u'add, edit due date, completed/re-open actions.')


@component.adapter(ITask, IPrincipalAssignedEvent)
def taskAssigned(object, ev):
    # subscribe assigned principal
    notification = getAdapter(object, ITasksNotification, 'tasks')
    if not notification.isSubscribedInParents(object, ev.principal):
        notification = getAdapter(
            object, IAssigneeTasksNotification, 'assigneetasks')
        if not notification.isSubscribedInParents(object, ev.principal):
            notification.subscribe(ev.principal)


def taskHandler(task, ev):
    if IDraftedContent.providedBy(task):
        return

    principals = sendNotification('tasks', task, ev)

    assignments = IAssignments(task, None)
    if assignments is not None:
        principals = [principal.id for principal in
                      assignments.getAssignees()
                      if principal.id not in principals]
        sendNotification(
            'assigneetasks', task, ev, principal={'any_of': principals})


@component.adapter(ITask, IObjectModifiedEvent)
def taskModified(task, ev):
    if IDraftedContent.providedBy(task) or not ev.descriptions:
        return

    principals = sendNotification('tasks', task, ev)

    principals = [principal.id for principal in
                  IAssignments(task).getAssignees()
                  if principal.id not in principals]
    sendNotification(
        'assigneetasks', task, ev, principal={'any_of': principals})


@component.adapter(ITaskComment, IIntIdAddedEvent)
def taskCommentAdded(comment, ev):
    task = comment.content
    if IDraftedContent.providedBy(task):
        return

    principals = sendNotification('tasks', task, comment)

    principals = [principal.id for principal in
                  IAssignments(task).getAssignees()
                  if principal.id not in principals]
    sendNotification(
        'assigneetasks', task, comment, principal={'any_of': principals})
