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
from zope import interface
from persistent import Persistent
from zope.location import Location
from zope.component import getUtility
from zope.app.intid.interfaces import IIntIds

from interfaces import ITaskComment


class TaskComment(Persistent, Location):
    interface.implements(ITaskComment)

    date = None
    anonymous = False
    attachments = ()

    def __init__(self, author, comment, changes, attachments):
        self.comment = comment
        self.author = author
        self.changes = changes
        self.attachments = tuple(attachments)

    @property
    def content(self):
        return self.__parent__.__parent__

    def getAttachments(self):
        if self.attachments:
            ids = getUtility(IIntIds)
            attachs = []
            for attach in self.attachments:
                ob = ids.queryObject(attach)
                if ob is not None:
                    attachs.append(ob)

            return attachs
        return []
