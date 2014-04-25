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
import datetime
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
from zojax.workflow.interfaces import IWorkflowState
from zojax.statusmessage.interfaces import IStatusMessage

from zojax.project.interfaces import _, ITasks
from zojax.project.browser.interfaces import ITasksTable, IComplatedTasksTable
from zojax.project.task import Task
from zojax.project.vocabulary import priorityVocabulary

from zope.app.component.hooks import getSite, setSite
import zope, transaction
from zojax.principal.users.interfaces import IUsersPlugin
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

from zope import event
from zojax.content.type.interfaces import IContentType
from zope.lifecycleevent import ObjectModifiedEvent, ObjectCreatedEvent
from zojax.richtext.field import RichTextData


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
    name='tasks.active'

    def initDataset(self):
        self.dataset = getUtility(ICatalog).searchResults(
            type={'any_of': ('project.task',),},
            projectTaskState = {'any_of': (1,)},
            searchContext = self.context, sort_on='projectTaskDate')


class CompletedTasks(Tasks):
    interface.implements(IComplatedTasksTable)

    msgEmptyTable = _('There are no completed tasks.')
    name='tasks.completed'

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
            return getattr(principal,'title', default)


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


class PriorityColumn(Column):
    component.adapts(interface.Interface, interface.Interface, ITasksTable)

    name = u'priority'
    title = _(u'Priority')
    cssClass = u't-task-priority'

    def query(self, default=None):
        return self.content.priority

    def render(self):
        try:
            return priorityVocabulary.getTerm(self.content.priority).title
        except LookupError:
            return u'---'


class StatusColumn(Column):
    component.adapts(interface.Interface, interface.Interface, ITasksTable)

    name = u'status'
    title = _(u'Status')
    cssClass = u't-task-status'

    def update(self):
        self.vocs = {}

    def query(self, default=None):
        return IWorkflowState(self.content).getState().title

    def render(self):
        return IWorkflowState(self.content).getState().title


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


class AddTasks(object):
    def update(self):
        context = self.context
        #gel all users
        users_list = ''
        users_map = {}
        msg = ''
        users = zope.component.getUtility(IUsersPlugin)
        for user in users.values():
            users_map[str(user.title)]=str(user.id)
            users_list= users_list+str(user.title)+'|@|'
        self.users_list = users_list

        #get milestone
        mst = context.get('milestones')
        ids = getUtility(IIntIds)

        milestones = []
        milestone_str = 'no value|-|--NOVALUE--|@|'
        for milestone in mst.values():
            id = ids.getId(removeAllProxies(milestone))
            milestones.append(milestone.title+'|-|'+str(id))
        milestones.sort()
        for milestone in milestones:
            milestone_str = milestone_str + milestone + '|@|'
        self.milestones = milestone_str[:-3]

        #get priorities
        self.priorities = priorityVocabulary

        #get fields
        post_title = []
        post_milestone = []
        post_responsible = []
        post_priority = []

        if self.request.form:
            for field in self.request.form:
                if field == 't_title':
                    if type(self.request.form[field]) == list:
                        post_title = self.request.form[field]
                    else:
                        post_title.append(self.request.form[field])
                if field == 't_milestone':
                    if type(self.request.form[field]) == list:
                        post_milestone = self.request.form[field]
                    else:
                        post_milestone.append(self.request.form[field])
                if field == 't_responsible':
                    if type(self.request.form[field]) == list:
                        post_responsible = self.request.form[field]
                    else:
                        post_responsible.append(self.request.form[field])
                if field == 't_priority':
                    if type(self.request.form[field]) == list:
                        post_priority = self.request.form[field]
                    else:
                        post_priority.append(self.request.form[field])


        if self.request.method == 'POST':
            error = False
            for index, name in enumerate(post_title):
                taskCt = component.getUtility(IContentType, name='project.task')
                task = taskCt.create(state=1)
                if name.strip() == '':
                    error = True
                    msg += 'Error: Responsible is wrong! \n'
                else:
                    task.title = name.strip()
                task.priority = int(post_priority[index])
                if post_milestone[index] != '--NOVALUE--':
                    try:
                        task.milestone = int(post_milestone[index])
                    except ValueError:
                        error = True
                        msg += 'Error: Milestone is wrong! \n'
                task.date = datetime.date.today()
                task.text = RichTextData()
                try:
                    uid = users_map[post_responsible[index]]
                except KeyError, IndexError:
                    error = True
                    msg += 'Error: Responsible is wrong!'

                if error == False:
                    taskCt.__bind__(self.context['tasks']).add(task)
                    event.notify(ObjectCreatedEvent(task))
                    assignments_new = IAssignments(task)
                    assignments_new.assign((uid,))
            if error == True:
                self.redirect('./add_tasks/')
            else:
                self.redirect('./tasks/')
