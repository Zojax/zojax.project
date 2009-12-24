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
from BTrees.Length import Length
from zope import interface, component, event
from zope.schema.fieldproperty import FieldProperty
from zope.security.proxy import removeSecurityProxy
from zope.cachedescriptors.property import Lazy
from zope.lifecycleevent import ObjectCreatedEvent
from zope.app.container.contained import NameChooser
from zojax.content.type.container import ContentContainer
from zojax.content.space.workspace import WorkspaceFactory

from interfaces import _, IProject
from interfaces import ITask, ITasks, ITasksFactory, ITaskAttributesConfig
from taskcategory import CategoryContainer


class Tasks(ContentContainer):
    interface.implements(ITasks, ITaskAttributesConfig)

    status = FieldProperty(ITaskAttributesConfig['status'])
    severity = FieldProperty(ITaskAttributesConfig['severity'])

    @Lazy
    def _next_id(self):
        next = Length(1)
        self._p_changed = True
        return next

    @property
    def nextId(self):
        id = self._next_id()
        self._next_id.change(1)
        return u'%0.5d'%id

    @property
    def category(self):
        category = self.get('category')
        if category is None:
            category = CategoryContainer(u'Category')
            event.notify(ObjectCreatedEvent(category))
            self['category'] = category
            category = self['category']
        return category


class TasksNameChooser(NameChooser):
    component.adapts(ITasks)

    def __init__(self, context):
        self.context = context

    def chooseName(self, name, object):
        return removeSecurityProxy(self.context).nextId


class TasksWorkspaceFactory(WorkspaceFactory):
    component.adapts(IProject)
    interface.implements(ITasksFactory)

    name = 'tasks'
    weight = 200
    title = _(u'Tasks')
    description = _(u'Project tasks.')

    factory = Tasks
