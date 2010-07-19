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
from zojax.mail.interfaces import IMailer
"""

$Id$
"""
import types
from datetime import date
from email.Utils import formataddr

from zope import interface, component
from zope.proxy import removeAllProxies
from zope.component import getUtility, queryMultiAdapter
from zope.traversing.browser import absoluteURL
from zope.app.component.hooks import getSite
from zope.size.interfaces import ISized
from zope.app.intid.interfaces import IIntIds
from zope.dublincore.interfaces import IDCTimes
from zope.schema.interfaces import IVocabularyFactory

from zojax.ownership.interfaces import IOwnership
from zojax.assignment.interfaces import IAssignments
from zojax.workflow.interfaces import IWorkflowState
from zojax.principal.profile.interfaces import IPersonalProfile
from zojax.project.vocabulary import priorityVocabulary
from zojax.project.interfaces import ITask, ITaskAttributes


class TaskNotification(object):

    status = None
    severity = None
    categories = None
    milestone = None
    overdue = None

    def update(self):
        super(TaskNotification, self).update()

        context = removeAllProxies(self.context)
        request = self.request
        principal = self.request.principal
        ids = getUtility(IIntIds)

        self.name = context.__name__

        mailer = getUtility(IMailer)

        profile = IPersonalProfile(principal, None)
        if profile is not None and profile.email:
            author = profile.title
            self.author = author
            self.addHeader(u'To', formataddr((author, profile.email),))
        else:
            self.author = principal.title or principal.id

        self.addHeader(u'From', formataddr((self.author, mailer.email_from_address),))

        self.addHeader(u'In-Reply-To', u'<%s@zojax.net>'%ids.getId(context))

        self.url = '%s/'%absoluteURL(context, request)
        self.title = u'%s %s'%(self.name, context.title)
        self.project = context.__parent__.__parent__

        # project
        self.projectTitle = self.project.title
        self.projectUrl = u'%s/'%absoluteURL(self.project, request)

        # status
        self.status = IWorkflowState(context).getState().title

        # severity
        voc = getUtility(IVocabularyFactory, 'project.task.severity')(context)
        if voc:
            try:
                self.severity = voc.getTerm(context.severity).title
            except LookupError:
                self.severity = u'---'

        # categories
        voc = getUtility(IVocabularyFactory, 'project.task.categories')(context)
        if voc:
            categories = []
            for cat in context.category:
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

        # owner
        self.owner = IOwnership(context).owner

        # date
        if self.context.state == 1:
            today = date.today()
            if context.date < today:
                self.overdue = today - context.date

        # assignees
        assignments = []
        for principal in IAssignments(context).getAssignees():
            assignments.append(principal.title)
        assignments.sort()
        self.assignments = assignments

    def text(self):
        text = getattr(self.context.text,'cooked', '')

        if u'src="@@content.attachment/' in text:
            s = u'src="%s/@@content.attachment/'%absoluteURL(
                getSite(), self.request)
            text = text.replace(u'src="@@content.attachment/', s)

        return text


class TaskAddedNotification(TaskNotification):

    @property
    def subject(self):
        return u'%s: Task created "%s"'%(self.project.title, self.context.title)


class TaskDeletedNotification(object):

    def update(self):
        super(TaskDeletedNotification, self).update()

        context = removeAllProxies(self.context)
        request = self.request
        principal = self.request.principal

        self.name = context.__name__

        profile = IPersonalProfile(principal, None)
        if profile is not None and profile.email:
            author = profile.title
            self.author = author
            self.addHeader(u'To', formataddr((author, profile.email),))
            self.addHeader(u'From', formataddr((author, profile.email),))
        else:
            self.author = principal.title or principal.id

        self.url = '%s/'%absoluteURL(context, request)
        self.project = context.__parent__.__parent__

        # project
        self.projectTitle = self.project.title
        self.projectUrl = u'%s/'%absoluteURL(self.project, request)

    @property
    def subject(self):
        return u'%s: Task deleted "%s"'%(self.project.title, self.context.title)


class CommentNotificationMail(TaskNotification):

    def update(self):
        super(CommentNotificationMail, self).update()

        changes = []
        for field, data in self.context0.changes.items():
            if field in ITask:
                title = ITask[field].title
            elif field in ITaskAttributes:
                title = ITaskAttributes[field].title
            elif field == 'status':
                title = 'Workflow state'
            else:
                continue

            if type(data[0]) in (types.TupleType, types.ListType):
                oldvalue = u', '.join(data[0])
            else:
                oldvalue = data[0]

            if type(data[1]) in (types.TupleType, types.ListType):
                newvalue = u', '.join(data[1])
            else:
                newvalue = data[1]

            changes.append(
                (title, {'title': title, 'old': oldvalue, 'new': newvalue}))

        changes.sort()
        self.changes = [info for _t, info in changes]

        # attachments
        attachments = []
        for attach in self.context0.getAttachments():
            info = {'id': attach.__name__,
                    'title': attach.title or attach.__name__,
                    'description': attach.description,
                    'size': ISized(attach).sizeForDisplay(),
                    'attach': attach}
            attachments.append(info)

        self.attachments = attachments

    @property
    def subject(self):
        if not self.context0.changes:
            return u'%s: New comment added to "%s"'%(
                self.project.title, self.context.title)
        else:
            return u'%s: Task modified "%s"'%(
                self.project.title, self.context.title)

    @property
    def messageId(self):
        return u'<%s@zojax>'%getUtility(IIntIds).getId(self.context0)
