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
from datetime import date, timedelta
from zope import component, interface, event
from zope.component import getUtility, queryMultiAdapter
from zope.proxy import removeAllProxies
from zope.location import LocationProxy
from zope.traversing.browser import absoluteURL
from zope.app.intid.interfaces import IIntIds
from zope.dublincore.interfaces import IDCTimes
from zope.contentprovider.interfaces import IContentProvider
from zope.lifecycleevent import ObjectModifiedEvent
from zope.security.checker import ProxyFactory
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces.browser import IBrowserPublisher

from zojax.table.column import Column
from zojax.catalog.interfaces import ICatalog
from zojax.ownership.interfaces import IOwnership
from zojax.assignment.interfaces import IAssignments
from zojax.statusmessage.interfaces import IStatusMessage

from zojax.project.interfaces import _, IMilestone
from zojax.project.browser.tasks import Tasks, TitleColumn
from zojax.project.browser.interfaces import IMilestoneTasksTable


class MilestoneTasks(Tasks):
    interface.implementsOnly(IMilestoneTasksTable)
    component.adapts(IMilestone, interface.Interface, interface.Interface)

    pageSize = 50
    enabledColumns = ('id', 'title', 'author',
                      'category', 'severity', 'status', 'date', 'assigned')
    msgEmptyTable = _('There are no active tasks.')

    def initDataset(self):
        id = getUtility(IIntIds).getId(removeAllProxies(self.context))

        self.dataset = getUtility(ICatalog).searchResults(
            type={'any_of': ('project.task',),},
            projectTaskState = {'any_of': (1,)},
            projectTaskMilestone = {'any_of': (id,)},
            searchContext = self.context.__parent__.__parent__,
            sort_on='projectTaskDate')


class CompletedMilestoneTasks(Tasks):
    interface.implementsOnly(IMilestoneTasksTable)
    component.adapts(IMilestone, interface.Interface, interface.Interface)

    pageSize = 50
    enabledColumns = ('id', 'title', 'author',
                      'category', 'severity', 'status', 'date', 'assigned')
    msgEmptyTable = _('There are no completed tasks.')

    def initDataset(self):
        id = getUtility(IIntIds).getId(removeAllProxies(self.context))

        self.dataset = getUtility(ICatalog).searchResults(
            type={'any_of': ('project.task',),},
            projectTaskState = {'any_of': (2,)},
            projectTaskMilestone = {'any_of': (id,)},
            searchContext = self.context.__parent__.__parent__,
            sort_on='projectTaskDate')


class BrowseActiveMilestoneTasks(Tasks):
    interface.implementsOnly(IMilestoneTasksTable)
    component.adapts(IMilestone, interface.Interface, interface.Interface)

    pageSize = 0
    enabledColumns = ('id', 'title', 'status', 'date', 'modified', 'assigned')
    msgEmptyTable = u''

    def initDataset(self):
        id = getUtility(IIntIds).getId(removeAllProxies(self.context))
        self.dataset = getUtility(ICatalog).searchResults(
            type={'any_of': ('project.task',),},
            projectTaskState = {'any_of': (1,)},
            projectTaskMilestone = {'any_of': (id,)},
            searchContext = self.context.__parent__.__parent__,
            sort_on='projectTaskDate')


class BrowseCompletedMilestoneTasks(Tasks):
    interface.implementsOnly(IMilestoneTasksTable)
    component.adapts(IMilestone, interface.Interface, interface.Interface)

    pageSize = 0
    enabledColumns = ('id', 'title', 'status', 'date', 'modified')
    msgEmptyTable = u''

    def initDataset(self):
        id = getUtility(IIntIds).getId(removeAllProxies(self.context))
        self.dataset = getUtility(ICatalog).searchResults(
            type={'any_of': ('project.task',),},
            projectTaskState = {'any_of': (2,)},
            projectTaskMilestone = {'any_of': (id,)},
            searchContext = self.context.__parent__.__parent__,
            sort_on='projectTaskDate')


class TitleColumn(TitleColumn):
    component.adapts(IMilestone, interface.Interface, IMilestoneTasksTable)

    def update(self):
        self.url = absoluteURL(self.context, self.request)

    def render(self):
        return u'<a href="%s/%s/">%s</a>'%(
            self.url, self.content.__name__, self.query())


class MilestoneView(object):

    overdue = None
    percent = 100

    def update(self):
        context = self.context

        # times
        dc = IDCTimes(context)
        self.created = dc.created
        self.modified = dc.modified

        # owner
        self.owner = IOwnership(context).owner

        # date
        if self.context.state == 1:
            today = date.today()
            if context.date < today:
                self.overdue = today - context.date

        # assignees
        assignments = []
        for principal in IAssignments(self.context).getAssignees():
            assignments.append(principal.title)
        assignments.sort()
        self.assignments = assignments

        # tables
        self.tasks = queryMultiAdapter(
            (context, self.request, self), IContentProvider, 'project.tasks')
        self.tasks.update()

        self.completed = queryMultiAdapter(
            (context, self.request, self),
            IContentProvider, 'project.tasks.completed')
        self.completed.update()

        # stats
        self.tcompleted = len(self.completed.dataset)
        self.total = len(self.tasks.dataset) + self.tcompleted
        if self.total > 0:
            self.percent = int(self.tcompleted/(self.total/100.0))


class MilestonePublisher(object):
    interface.implements(IBrowserPublisher)
    component.adapts(IMilestone, interface.Interface)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def publishTraverse(self, request, name):
        view = queryMultiAdapter((self.context, request), name=name)
        if view is not None:
            return view

        tasks = self.context.__parent__.__parent__.get('tasks')
        if tasks is not None:
            task = tasks.get(name)
            if task is not None:
                id = getUtility(IIntIds).getId(removeAllProxies(self.context))
                if task.milestone == id:
                    return LocationProxy(
                        removeAllProxies(task), self.context, name)

        raise NotFound(self.context, name, request)

    def browserDefault(self, request):
        return self.context, ('index.html',)


class CompleteMilestone(object):

    def update(self):
        self.table = queryMultiAdapter(
            (self.context, self.request, self), IContentProvider, 'project.tasks')
        self.table.update()

        if 'button.complete' in self.request:
            self.context.completeTask()
            event.notify(ObjectModifiedEvent(self.context))
            IStatusMessage(self.request).add(_('Milestone has been completed.'))
            self.redirect('./')
            return

        if 'button.cancel' in self.request:
            self.redirect('./')
            return

        if not self.table:
            self.context.completeTask()
            event.notify(ObjectModifiedEvent(self.context))

            IStatusMessage(self.request).add(_('Milestone has been completed.'))
            self.redirect('./')


class ReopenMilestone(object):

    def update(self):
        if self.context.state != 1:
            self.context.reopenTask()
            event.notify(ObjectModifiedEvent(self.context))

            IStatusMessage(self.request).add(_('Milestone has been reopened.'))

        self.redirect('./')
