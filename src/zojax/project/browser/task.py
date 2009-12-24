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

from zope import event
from zope.component import getUtility
from zope.proxy import removeAllProxies
from zope.security import checkPermission
from zope.app.intid.interfaces import IIntIds
from zope.traversing.browser import absoluteURL
from zope.dublincore.interfaces import IDCTimes
from zope.schema.interfaces import IVocabularyFactory
from zope.lifecycleevent import ObjectModifiedEvent
from zope.size.interfaces import ISized
from zope.dublincore.interfaces import IDCTimes

from zojax.layoutform import Fields, PageletEditSubForm
from zojax.ownership.interfaces import IOwnership
from zojax.assignment.interfaces import IAssignments
from zojax.statusmessage.interfaces import IStatusMessage
from zojax.content.attachment.interfaces import IAttachmentsExtension
from zojax.principal.profile.interfaces import IPersonalProfile
from zojax.workflow.interfaces import IWorkflowState
from zojax.content.forms.content import ContentBasicFields

from zojax.project.vocabulary import priorityVocabulary

from zojax.project.interfaces import _, ITask, ITaskAssignee
from zojax.project.interfaces import ITaskAttributes, ITaskAttributesConfig


class TaskBasicForm(ContentBasicFields):

    fields = Fields(ITask, ITaskAssignee).omit('title')


class TaskAttributesForm(PageletEditSubForm):

    @property
    def fields(self):
        fields = Fields(ITaskAttributes)

        content = self.getContent()

        voc = getUtility(IVocabularyFactory, 'project.task.severity')(content)
        if not voc:
            fields = fields.omit('severity')

        voc = getUtility(IVocabularyFactory, 'project.task.categories')(content)
        if not voc:
            fields = fields.omit('category')

        return fields

    def getContent(self):
        return self.context


class TaskAttributesConfigureForm(PageletEditSubForm):

    fields = Fields(ITaskAttributesConfig)

    def getContent(self):
        return self.context


class TaskView(object):

    status = None
    severity = None
    categories = None
    milestone = None
    overdue = None

    def update(self):
        context = self.context
        task = removeAllProxies(context)
        self.name = task.__name__

        # status
        self.status = IWorkflowState(context).getState().title

        # severity
        voc = getUtility(IVocabularyFactory, 'project.task.severity')(task)
        if voc:
            try:
                self.severity = voc.getTerm(context.severity).title
            except LookupError:
                self.severity = u'---'

        # categories
        voc = getUtility(IVocabularyFactory, 'project.task.categories')(task)
        if voc:
            categories = []
            for cat in context.category or ():
                try:
                    categories.append(voc.getTerm(cat).title)
                except LookupError:
                    pass
            if not categories:
                categories.append(u'---')

            self.categories = categories

        # priority
        try:
            self.priority = priorityVocabulary.getTerm(context.priority).title
        except LookupError:
            self.priority = u'---'

        # times
        dc = IDCTimes(context)
        self.created = dc.created
        self.modified = dc.modified

        # milestone
        if context.milestone:
            try:
                milestone = getUtility(IIntIds).queryObject(context.milestone)
                if milestone is not None:
                    self.milestone = milestone.title
                    self.milestoneURL = u'%s/'%absoluteURL(
                        milestone, self.request)
            except:
                pass

        # project
        project = removeAllProxies(context).__parent__.__parent__
        self.project = project.title
        self.projectURL = u'%s/'%absoluteURL(project, self.request)

        # owner
        self.owner = IOwnership(context).owner

        # date
        if self.context.state == 1:
            today = date.today()
            if context.date < today:
                self.overdue = today - context.date

        # assignees
        assignments = []
        for principal in IAssignments(task).getAssignees():
            assignments.append(principal.title)
        assignments.sort()
        self.assignments = assignments

        # attachments
        attachments = []

        for attach in IAttachmentsExtension(task).values():
            ownership = IOwnership(attach)
            profile = IPersonalProfile(ownership.owner, None)

            info = {'id': attach.__name__,
                    'title': attach.title or attach.__name__,
                    'description': attach.description,
                    'size': ISized(attach).sizeForDisplay(),
                    'created': IDCTimes(attach).created,
                    'owner': getattr(profile, 'title', _('Unknown')),
                    'attach': attach,
                    }

            attachments.append((info['created'], info))

        attachments.sort()
        self.attachments = [attach for _c, attach in attachments]


class TaskDelete(object):

    def update(self):
        self.task = removeAllProxies(self.context)

        if not checkPermission('zojax.DeleteContent', self.task):
            raise Unauthorized

        if 'form.delete.content' in self.request:
            del self.task.__parent__[self.task.__name__]

            IStatusMessage(self.request).add(_('Content has been deleted.'))
            self.redirect('../')
            return

        elif 'form.delete.cancel' in self.request:
            self.redirect('./')
            return

        super(TaskDelete, self).update()


class CompleteTask(object):

    def update(self):
        if self.context.state != 2:
            self.context.completeTask()
            event.notify(ObjectModifiedEvent(self.context))

            IStatusMessage(self.request).add(_('Task has been completed.'))

        self.redirect('./')


class ReopenTask(object):

    def update(self):
        if self.context.state != 1:
            self.context.reopenTask()
            event.notify(ObjectModifiedEvent(self.context))

            if self.context.milestone:
                try:
                    milestone = getUtility(IIntIds).queryObject(
                        self.context.milestone)
                except:
                    milestone = None
                if milestone is not None:
                    if milestone.state != 1:
                        removeAllProxies(milestone).reopenTask()
                        event.notify(ObjectModifiedEvent(milestone))
                        IStatusMessage(self.request).add(
                            _('Milestone and Task have been reopened.'))
                        self.redirect('./')
                        return

            IStatusMessage(self.request).add(_('Task has been reopened.'))

        self.redirect('./')
