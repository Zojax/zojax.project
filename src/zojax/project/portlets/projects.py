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
from zope.dublincore.interfaces import IDCTimes
from zope.component import queryUtility

from zojax.project.types import types
from zojax.content.space.interfaces import IContentSpace
from zojax.members.interfaces import IMembersAware
from zojax.ownership.interfaces import IOwnership
from zojax.catalog.interfaces import ICatalog
from zojax.content.schema.interfaces import IContentSchema

class ProjectsPortlet(object):

    items = None

    def update(self):
        catalog = queryUtility(ICatalog)
        if catalog is not None:
            results = catalog.searchResults(
                    traversablePath={'any_of': (self.getContext(),)},
                    sort_order='reverse', sort_on='modified',
                    type={'any_of': ('content.project', \
                                     'content.standaloneproject',)},
                    isDraft={'any_of': (False,)},)[:self.number]

            if results:
                self.items = results

    def getContext(self):
        context = self.context

        while not IContentSpace.providedBy(context):
            context = context.__parent__
            if context is None:
                return

        return context

    def getContentSchema(self, project):
        return IContentSchema(project)

    def getProjectInfo(self, project):
        context = project

        dc = IDCTimes(context)
        principal = getattr(IOwnership(context, None), 'owner', None)

        info = {
            'title': context.title,
            'description': context.description,
            'owner': principal,
            'created': dc.created,
            'members': None,
            'default': not bool(context.logo),
            'ptype': types.getTerm(context.ptype),
            'project': context}

        if IMembersAware.providedBy(context):
            info['members'] = len(context.members)

        return info

    def isAvailable(self):
        return bool(self.items)
