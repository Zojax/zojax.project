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
import cgi
from datetime import date
from zope import interface, component
from zope.proxy import removeAllProxies
from zope.component import getUtility, getUtilitiesFor
from zope.traversing.browser import absoluteURL
from zope.security.proxy import removeSecurityProxy
from zope.schema.interfaces import IVocabularyFactory
from zope.dublincore.interfaces import IDCTimes
from zope.app.intid.interfaces import IIntIds

from zojax.table.table import Table
from zojax.table.column import Column
from zojax.catalog.interfaces import ICatalog
from zojax.ownership.interfaces import IOwnership
from zojax.assignment.interfaces import IAssignments
from zojax.principal.profile.interfaces import IPersonalProfile
from zojax.formatter.utils import getFormatter
from zojax.statusmessage.interfaces import IStatusMessage

from zojax.project.interfaces import _, ITasks
from zojax.project.browser.interfaces import ITasksTable, IComplatedTasksTable


class Tasks(Table):
    interface.implements(ITasksTable)
    component.adapts(ITasks, interface.Interface, interface.Interface)

    title = _('Tasks')

    cssClass = 'z-table project-tasks-table'
    pageSize = 30
    enabledColumns = ('id', 'title', 'author',
                      'milestone', 'category', 'severity',
                      'status', 'date', 'modified', 'assigned')
    msgEmptyTable = _('There are no active tasks.')

    def initDataset(self):
        self.dataset = getUtility(ICatalog).searchResults(
            type={'any_of': ('project.task',),},
            projectTaskState = {'any_of': (1,)},
            searchContext = self.context, sort_on='projectTaskDate')


class CompletedTasks(Tasks):
    interface.implements(IComplatedTasksTable)

    msgEmptyTable = _('There are no completed tasks.')

    def initDataset(self):
        self.dataset = getUtility(ICatalog).searchResults(
            type={'any_of': ('project.task',),},
            projectTaskState = {'any_of': (2,)},
            searchContext = self.context, sort_on='projectTaskDate')


class IdColumn(Column):
    component.adapts(interface.Interface, interface.Interface, ITasksTable)

    name = u'id'
    title = _(u'Task id')
    cssClass = u't-task-id'

    def query(self, default=None):
        return self.content.__name__

    def render(self):
        return self.query()


class TitleColumn(Column):
    component.adapts(interface.Interface, interface.Interface, ITasksTable)

    name = 'title'
    title = u'Title'
    cssClass = u't-task-title'

    def query(self, default=None):
        return self.content.title

    def render(self):
        return u'<a href="%s/">%s</a>'%(
            absoluteURL(self.content, self.request), self.query())


class AuthorColumn(Column):
    component.adapts(interface.Interface, interface.Interface, ITasksTable)

    title = _(u'Submitted by')

    def query(self, default=None):
        principal = IOwnership(self.content).owner

        if principal is not None:
            request = self.request
            profile = IPersonalProfile(principal, None)
            if profile is not None:
                return profile.title
        else:
            return principal.title


class CreatedColumn(Column):
    component.adapts(interface.Interface, interface.Interface, ITasksTable)

    name = 'created'
    title = _(u'Submitted')

    def update(self):
        self.formatter = getFormatter(self.request,'fancyDatetime','medium')

    def query(self, default=None):
        return self.formatter.format(IDCTimes(self.content).created)


class ModifiedColumn(Column):
    component.adapts(interface.Interface, interface.Interface, ITasksTable)

    name = 'modified'
    title = _(u'Modified')
    cssClass = u't-task-modified'

    def update(self):
        self.formatter = getFormatter(self.request, 'date', 'short')

    def query(self, default=None):
        return self.formatter.format(IDCTimes(self.content).modified)


class MilestoneColumn(Column):
    component.adapts(interface.Interface, interface.Interface, ITasksTable)

    name = u'milestone'
    title = _(u'Milestone')
    cssClass = u't-task-milestone'

    def update(self):
        self.milestones = {}
        self.ids = getUtility(IIntIds)

    def query(self, default=None):
        return self.content.milestone

    def render(self):
        milestone = self.content.milestone
        if milestone not in self.milestones:
            try:
                self.milestones[milestone] = self.ids.queryObject(milestone)
            except:
                self.milestones[milestone] = None

        milestone = self.milestones[milestone]

        if milestone is not None:
            return milestone.title
        else:
            return u''


class SeverityColumn(Column):
    component.adapts(interface.Interface, interface.Interface, ITasksTable)

    name = u'severity'
    title = _(u'Severity')
    cssClass = u't-task-severity'

    def update(self):
        self.vocs = {}

    def query(self, default=None):
        return self.content.severity

    def render(self):
        tasks = removeAllProxies(self.content.__parent__)
        if tasks in self.vocs:
            voc = self.vocs[tasks]
        else:
            voc = getUtility(
                IVocabularyFactory, 'project.task.severity')(tasks)
            self.vocs[tasks] = voc

        try:
            term = voc.getTerm(self.query())
            return term.title
        except:
            return u'---'

    def isAvailable(self):
        return bool(self.voc)


class StatusColumn(Column):
    component.adapts(interface.Interface, interface.Interface, ITasksTable)

    name = u'status'
    title = _(u'Status')
    cssClass = u't-task-status'

    def update(self):
        self.vocs = {}

    def query(self, default=None):
        return self.content.status

    def render(self):
        tasks = removeAllProxies(self.content.__parent__)
        if tasks in self.vocs:
            voc = self.vocs[tasks]
        else:
            voc = getUtility(
                IVocabularyFactory, 'project.task.status')(tasks)
            self.vocs[tasks] = voc

        try:
            term = voc.getTerm(self.query())
            return term.title
        except:
            return u'---'

    def isAvailable(self):
        return bool(self.voc)


class DateColumn(Column):
    component.adapts(interface.Interface, interface.Interface, ITasksTable)

    name = 'date'
    title = _(u'Due date')

    def update(self):
        self.today = date.today()
        self.fancyDatetime = getFormatter(self.request, 'date', 'short')

    def __bind__(self, content, globalenviron, environ):
        clone = super(DateColumn, self).__bind__(content, globalenviron, environ)

        if content.state == 1:
            if content.date < self.today:
                clone.cssClass = 't-task-overdue'

        return clone

    def query(self, default=None):
        date = self.content.date
        if date:
            return self.fancyDatetime.format(date)
        else:
            return u'---'


class CategoryColumn(Column):
    component.adapts(interface.Interface, interface.Interface, ITasksTable)

    name = 'category'
    title = _(u'Category')
    cssClass = u't-task-category'

    def update(self):
        self.voc = getUtility(
            IVocabularyFactory, 'project.task.categories')(self.context)

    def query(self, default=None):
        return self.content.category or ()

    def render(self):
        category = []
        for cat in self.query():
            try:
                term = self.voc.getTerm(cat)
                category.append(term.title)
            except LookupError:
                pass

        if category:
            return u', '.join(category)

        else:
            return u''

    def isAvailable(self):
        return bool(self.voc)


class AssignedColumn(Column):
    component.adapts(interface.Interface, interface.Interface, ITasksTable)

    name = 'assigned'
    title = _(u'Assigned to')

    def query(self, default=None):
        assignments = []
        for principal in IAssignments(self.content).getAssignees():
            assignments.append(principal.title)
        assignments.sort()
        return assignments

    def render(self):
        return ', '.join([cgi.escape(a) for a in self.query()])
