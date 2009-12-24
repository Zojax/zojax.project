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
from zope import interface, component, event
from zope.proxy import removeAllProxies
from zope.traversing import api
from zope.app.component.hooks import getSite
from zope.schema.fieldproperty import FieldProperty
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

from zojax.members.interfaces import IMembersAware
from zojax.content.type.item import PersistentItem
from zojax.assignment.interfaces import IAssigneesProvider
from zojax.content.type.interfaces import IDraftedContent
from zojax.content.type.interfaces import ISearchableContent
from zojax.content.type.searchable import ContentSearchableText
from zojax.permissionsmap.interfaces import IObjectPermissionsMapsManager
from zojax.content.discussion.extension import getCommentsText
from zojax.content.attachment.indexes import getAttachmentsContent

from interfaces import StateChangedEvent
from interfaces import ITask, IState, ITaskAttributes, ITaskAttributesConfig


class Task(PersistentItem):
    interface.implements(ITask, ITaskAttributes, IState)

    state = FieldProperty(IState['state'])
    status = FieldProperty(ITaskAttributes['status'])
    severity = FieldProperty(ITaskAttributes['severity'])
    priority = FieldProperty(ITaskAttributes['priority'])
    category = FieldProperty(ITaskAttributes['category'])
    milestone = 0

    def reopenTask(self):
        self.state = 1
        event.notify(StateChangedEvent(self, 1))

    def completeTask(self):
        self.state = 2
        event.notify(StateChangedEvent(self, 2))


@component.adapter(ITask)
@interface.implementer(ITaskAttributesConfig)
def taskAttributesConfig(task):
    if IDraftedContent.providedBy(task):
        location = task.__parent__.getLocation()
        if ITaskAttributesConfig.providedBy(location):
            return location
    else:
        return removeAllProxies(task).__parent__


class TaskAssigneesProvider(object):
    component.adapts(ITask)
    interface.implements(IAssigneesProvider)

    def __init__(self, task):
        self.task = task

    def assignees(self):
        task = removeAllProxies(self.task)

        if IDraftedContent.providedBy(task):
            tasks = task.__parent__.getLocation()
            project = getattr(tasks, '__parent__', None)
        else:
            project = task.__parent__.__parent__

        group = IMembersAware(project, None)
        if group is None:
            return []

        return removeAllProxies(group.members).keys()


@component.adapter(ITask, IObjectModifiedEvent)
def taskModified(task, ev):
    if task.state == 1:
        name = u'project.task.active'
    else:
        name = u'project.task.completed'

    IObjectPermissionsMapsManager(removeAllProxies(task)).set((name,))


@component.adapter(ITask)
@interface.implementer(ISearchableContent)
def taskSearchable(task):
    return api.traverse(getSite(), api.getPath(removeAllProxies(task)))


class TaskSearchableText(ContentSearchableText):
    component.adapts(ITask)

    def getSearchableText(self):
        item = self.content
        title = item.title.strip()
        description = item.description.strip()
        comments = getCommentsText(item)
        attachments = getAttachmentsContent(item)

        text =  u' '.join(
            [s for s in [title, description, comments, attachments] if s])
        try:
            return text + u' ' + self.content.text.text
        except AttributeError:
            return text
