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
import cgi, types, os
from pytz import utc
from datetime import datetime

from zope import interface, schema, component, event
from zope.interface.common.idatetime import ITZInfo
from zope.i18n import translate
from zope.proxy import removeAllProxies
from zope.component import getUtility, getMultiAdapter
from zope.security import checkPermission
from zope.traversing.browser import absoluteURL
from zope.lifecycleevent import ObjectModifiedEvent, ObjectCreatedEvent
from zope.schema.interfaces import IVocabularyFactory
from zope.publisher.browser import FileUpload
from zope.dublincore.interfaces import IDCTimes
from zope.size.interfaces import ISized
from zope.app.container.interfaces import INameChooser
from zope.app.intid.interfaces import IIntIds
from zope.app.security.interfaces import IAuthentication, PrincipalLookupError

from zojax.filefield.data import FileData
from zojax.layoutform import button, Fields, PageletForm, interfaces
from zojax.assignment.interfaces import IAssignments
from zojax.content.discussion.interfaces import IContentDiscussion
from zojax.content.discussion.browser.comment import CommentView
from zojax.content.notifications.utils import getSubscribers
from zojax.principal.profile.interfaces import IPersonalProfile
from zojax.statusmessage.interfaces import IStatusMessage
from zojax.content.attachment.file import File
from zojax.content.attachment.image import Image
from zojax.content.attachment.interfaces import \
    IFile, IImage, IAttachmentsExtension
from zojax.resourcepackage.library import include

from zojax.project.interfaces import _
from zojax.project.interfaces import ITask, ITaskAttributes
from zojax.project.taskcomment import TaskComment
from zojax.project.vocabulary import priorityVocabulary


class ITaskCommentAdapter(interface.Interface):
    """ comment form """

    comment = schema.Text(
        title = _(u'Comment'),
        required = True)

    file = schema.Bytes(
        title = u'Select file/image',
        description = u'Upload multple files/images.',
        required = False)


class TaskCommentAdapter(object):
    component.adapts(ITask)
    interface.implements(ITaskCommentAdapter)

    def __init__(self, task):
        self.task = task
        self.comment = u''
        self.file = u''


class TaskCommentForm(PageletForm):
    """ task comment form """

    label = _('Add comment')
    updated = False
    severity = ()
    status = ()
    allowAssign = False
    allowAttributes = False
    allowAttachments = False
    manageSubscribers = False

    def update(self):
        if self.updated:
            return

        self.updated = True

        context = self.context
        if checkPermission('zojax.ModifyTaskStatus', context):
            self.severity = getUtility(
                IVocabularyFactory, 'project.task.severity')(context)

        if checkPermission('zojax.ModifyTaskAttributes', context):
            self.allowAttributes = True
            self.status = getUtility(
                IVocabularyFactory, 'project.task.status')(context)

        if checkPermission('zojax.AssignTo', context):
            self.allowAssign = True

        if checkPermission('zojax.AddContentAttachment', context):
            self.allowAttachments = True

        # subscribers
        auth = getUtility(IAuthentication)

        subs = getSubscribers(('tasks',), context)
        assignees = getSubscribers(('assigneetasks'), context)

        for pid in IAssignments(context).assignees:
            if pid in assignees:
                subs.add(pid)

        subscribers = []
        for subs in subs:
            try:
                principal = auth.getPrincipal(subs)
            except PrincipalLookupError:
                continue

            profile = IPersonalProfile(principal)

            subscribers.append(profile.title)

        subscribers.sort()
        self.subscribers = subscribers

        task = removeAllProxies(context)
        if checkPermission('zojax.ModifyContent', task.__parent__.__parent__):
            self.manageSubscribers = absoluteURL(
                task.__parent__.__parent__, self.request)

        super(TaskCommentForm, self).update()

        include('jquery-plugins')

        if 'file' in self.widgets:
            self.widgets['file'].klass = 'multi'

    @property
    def fields(self):
        fields = Fields(
            ITaskCommentAdapter,
            ITaskAttributes, ITask['assigned']).omit('category')

        if not self.status:
            fields = fields.omit('status')

        if not self.severity:
            fields = fields.omit('severity')

        if not self.allowAssign:
            fields = fields.omit('assigned')

        if not self.allowAttributes:
            fields = fields.omit('priority')

        if not self.allowAttachments:
            fields = fields.omit('file')

        return fields

    @button.buttonAndHandler(_('Add comment'))
    def addCommentHandler(self, action):
        request = self.request
        data, errors = self.extractData()

        if errors:
            IStatusMessage(request).add(self.formErrorsMessage, 'warning')
        else:
            task = self.context

            changes = {}
            if 'severity' in data and task.severity != data['severity']:
                try:
                    value = self.severity.getTerm(task.severity).title
                except:
                    value = u''
                changes['severity'] = [
                    value, self.severity.getTerm(data['severity']).title]
                task.severity = data['severity']

            if 'priority' in data and task.priority != data['priority']:
                try:
                    value = priorityVocabulary.getTerm(task.priority).title
                except:
                    value = u''
                changes['priority'] = [
                    value, priorityVocabulary.getTerm(data['priority']).title]
                task.priority = data['priority']

            if 'status' in data and task.status != data['status']:
                try:
                    value = self.status.getTerm(task.status).title
                except:
                    value = u''
                changes['status'] = [
                    value, self.status.getTerm(data['status']).title]
                task.status = data['status']

            if 'assigned' in data:
                assignments = IAssignments(task)

                oldassignees = []
                for principal in assignments.getAssignees():
                    oldassignees.append(principal.title)
                oldassignees.sort()

                assignees = list(assignments.assignees)
                assignees.sort()
                newassignees = list(data['assigned'])
                newassignees.sort()

                if assignees != newassignees:
                    assignments.assign(newassignees)

                    assignees = []
                    for principal in assignments.getAssignees():
                        assignees.append(principal.title)
                    assignees.sort()

                    changes['assigned'] = [oldassignees, assignees]

            # attachments
            comment = data['comment']
            if 'file' in self.widgets:
                attachments = IAttachmentsExtension(self.context)
                chooser = INameChooser(attachments)
                files = self.request.form[self.widgets['file'].name]
            else:
                files = []

            attachs = []

            for file in files:
                if isinstance(file, FileUpload):
                    filename = os.path.split(file.filename)[1].lower().strip()

                    fdata = FileData(file, filename)
                    if fdata.mimeType in ('image/jpeg','image/gif','image/png'):
                        attach = Image(title=filename, description=comment)
                    else:
                        attach = File(title=filename, description=comment)

                    attach.data = fdata
                    event.notify(ObjectCreatedEvent(attach))

                    name = chooser.chooseName(filename, attach)
                    attachments[name] = attach

                    attachs.append(attach)

            if attachs:
                ids = getUtility(IIntIds)
                attachs = [ids.getId(attach) for attach in attachs]

            event.notify(ObjectModifiedEvent(task))

            discussion = IContentDiscussion(task)
            if discussion.status != 1:
                discussion.status = 1

            comment = cgi.escape(data['comment']).replace('\n', '<br />')

            comment = TaskComment(
                request.principal.id, comment, changes, attachs)
            comment.date = datetime.now(ITZInfo(self.request, utc))

            comment = discussion.add(comment)

            IStatusMessage(self.request).add(_('Comment has been added.'))
            self.redirect('.')


class TaskComments(object):

    def update(self):
        discussion = IContentDiscussion(self.context)
        if discussion.status != 1:
            removeAllProxies(discussion).status = 1

        self.comments = list(discussion.values())

        self.postsAllowed = (discussion.status == 1 and
                             checkPermission('zojax.AddComment', self.context))
        if self.postsAllowed:
            self.reply = getMultiAdapter(
                (self.context, self.request), name='comment.html')
            self.reply.update()


class TaskCommentView(CommentView):

    hasImages = False

    def update(self):
        super(TaskCommentView, self).update()

        changes = []
        for field, data in self.context.changes.items():
            if field in ITask:
                title = ITask[field].title
            else:
                title = ITaskAttributes[field].title

            oldvalue = data[0]
            if type(data[0]) in (types.TupleType, types.ListType):
                oldvalue = u', '.join(data[0])

            newvalue = data[1]
            if type(data[1]) in (types.TupleType, types.ListType):
                newvalue = u', '.join(data[1])

            changes.append(
                (title, {'title': title, 'old': oldvalue, 'new': newvalue}))

        changes.sort()
        self.data = [info for _t, info in changes]

        # attachments
        attachments = []
        for attach in self.context.getAttachments():
            info = {'id': attach.__name__,
                    'title': attach.title or attach.__name__,
                    'description': attach.description,
                    'size': ISized(attach).sizeForDisplay(),
                    'image': False,
                    'attach': attach,
                    }
            if IImage.providedBy(attach):
                attach.preview.generatePreview(70, 70)
                info['image'] = True
                self.hasImages = True

            attachments.append(info)

        self.attachments = attachments
