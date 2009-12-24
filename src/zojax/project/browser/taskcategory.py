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
from zope import interface, component
from zope.traversing.browser import absoluteURL

from zojax.content.actions.action import Action

from zojax.project.interfaces import _, ITasks
from zojax.project.browser.interfaces import IAddCategoryAction
from zojax.project.browser.interfaces import IManageCategoriesAction


class AddCategory(Action):
    component.adapts(ITasks, interface.Interface)
    interface.implements(IAddCategoryAction)

    weight = 99999
    title = _(u'Add Category')
    permission = 'zojax.ModifyContent'

    @property
    def url(self):
        return '%s/+/project.task.category/'%absoluteURL(
            self.context.category, self.request)


class ManageCategories(Action):
    component.adapts(ITasks, interface.Interface)
    interface.implements(IManageCategoriesAction)

    weight = 999
    title = _(u'Manage categories')
    permission = 'zojax.ModifyContent'

    @property
    def url(self):
        return '%s/context.html'%absoluteURL(
            self.context.category, self.request)
