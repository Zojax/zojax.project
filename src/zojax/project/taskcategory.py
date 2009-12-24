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

from zope import interface, component
from zope.component import getUtility
from zope.proxy import removeAllProxies
from zope.cachedescriptors.property import Lazy
from zope.app.intid.interfaces import IIntIds
from zope.app.container.contained import NameChooser
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zojax.content.type.item import PersistentItem
from zojax.content.type.container import ContentContainer
from zojax.content.space.interfaces import ISpace
from zojax.content.draft.interfaces import IDraftContent

from interfaces import IProject, ITasks, ITaskCategory, ITaskCategoryContainer


class Category(PersistentItem):
    interface.implements(ITaskCategory)


class CategoryContainer(ContentContainer):
    interface.implements(ITaskCategoryContainer)

    @Lazy
    def _next_id(self):
        next = Length(1)
        self._p_changed = True
        return next

    @property
    def nextId(self):
        id = self._next_id()
        self._next_id.change(1)
        return u'%0.3d'%id


class CategoryContainerNameChooser(NameChooser):
    component.adapts(ITaskCategoryContainer)

    def __init__(self, context):
        self.context = context

    def chooseName(self, name, object):
        return removeAllProxies(self.context).nextId


class CategoriesVocabulary(object):
    interface.implements(IVocabularyFactory)

    def __call__(self, context):
        while True:
            if IProject.providedBy(context):
                break

            if IDraftContent.providedBy(context):
                context = context.getLocation()
                if not ITasks.providedBy(context):
                    context = None
                context = getattr(context, '__parent__', None)
                break

            context = getattr(context, '__parent__', None)
            if context is None:
                break

        if context is not None:
            context = context.get('tasks')
        if context is None:
            return SimpleVocabulary(())

        ids = getUtility(IIntIds)

        categories = []
        for category in context.category.values():
            id = ids.getId(removeAllProxies(category))

            term = SimpleTerm(id, str(id), category.title)
            term.description = category.description

            categories.append((category.title, term))

        categories.sort()
        return SimpleVocabulary([term for title, term in categories])
