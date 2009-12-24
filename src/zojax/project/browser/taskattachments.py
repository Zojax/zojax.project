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
import os.path
from zope import interface, schema, event
from zope.i18n import translate
from zope.size.interfaces import ISized
from zope.publisher.browser import FileUpload
from zope.dublincore.interfaces import IDCTimes
from zope.lifecycleevent import ObjectCreatedEvent
from zope.app.container.interfaces import INameChooser

from zojax.resourcepackage.library import include
from zojax.layoutform import button, Fields, PageletForm, interfaces
from zojax.filefield.data import FileData
from zojax.ownership.interfaces import IOwnership
from zojax.content.attachment.file import File
from zojax.content.attachment.image import Image
from zojax.content.attachment.interfaces import \
    IFile, IImage, IAttachmentsExtension
from zojax.content.notifications.utils import sendNotification
from zojax.statusmessage.interfaces import IStatusMessage

from zojax.project.interfaces import _
from zojax.project.notifications.interfaces import ITaskAttachments


class IUploadAttachments(interface.Interface):

    file = schema.Bytes(
        title = u'Select file/image',
        description = u'Upload multple files/images.',
        required = True)

    comment = schema.Text(
        title = u'Comment',
        default = u'',
        required = False)


class UploadAttachments(PageletForm):

    label = u'Upload files/images'

    fields = Fields(IUploadAttachments)

    ignoreContext = True

    def update(self):
        include('jquery-plugins')
        super(UploadAttachments, self).update()

        self.widgets['file'].klass = 'multi'

    @button.buttonAndHandler(_('Cancel'), provides=interfaces.ICancelAction)
    def cancelHandler(self, action):
        self.redirect('.')

    @button.buttonAndHandler(_('Upload'))
    def uploadHandler(self, action):
        data, errors = self.extractData()

        if errors:
            IStatusMessage(self.request).add(self.formErrorMessage, 'warning')
        else:
            comment = data['comment']
            files = self.request.form[self.widgets['file'].name]

            attachments = IAttachmentsExtension(self.context)
            chooser = INameChooser(attachments)

            attachs = []

            for file in files:
                if isinstance(file, FileUpload):
                    filename = os.path.split(file.filename)[1].lower().strip()

                    data = FileData(file, filename)
                    if data.mimeType in ('image/jpeg','image/gif','image/png'):
                        attach = Image(title=filename, description=comment)
                    else:
                        attach = File(title=filename, description=comment)

                    attach.data = data
                    event.notify(ObjectCreatedEvent(attach))

                    name = chooser.chooseName(filename, attach)
                    attachments[name] = attach

                    attachs.append(attach)

            sendNotification(
                'tasks', self.context, TaskAttachmentsInfo(comment, attachs))

            IStatusMessage(self.request).add(
                _('Attachments have been uploaded.'))
            self.redirect('.')


class TaskAttachments(object):

    def update(self):
        attachments = []

        for attach in IAttachmentsExtension(self.context).values():
            ownership = IOwnership(attach)

            info = {'id': attach.__name__,
                    'title': attach.title or attach.__name__,
                    'description': attach.description,
                    'size': translate(ISized(attach).sizeForDisplay()),
                    'created': IDCTimes(attach).created,
                    'owner': ownership.owner and ownership.owner.title or _('Unknown'),
                    'image': False,
                    'attach': attach,
                    }
            if IImage.providedBy(attach):
                attach.preview.generatePreview(70, 70)
                info['image'] = True

            attachments.append((info['created'], info))

        attachments.sort()
        self.attachments = [attach for _c, attach in attachments]


class TaskAttachmentsInfo(object):
    interface.implements(ITaskAttachments)

    def __init__(self, comment, attachments):
        self.comment = comment
        self.attachments = attachments
