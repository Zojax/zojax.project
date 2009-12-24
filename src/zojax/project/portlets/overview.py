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

from zojax.project.types import types
from zojax.project.interfaces import IProject
from zojax.members.interfaces import IMembersAware
from zojax.ownership.interfaces import IOwnership
from zojax.content.schema.interfaces import IContentSchema

from zojax.cache.view import cache
from zojax.cache.keys import ContextModified


class ProjectOverviewPortlet(object):

    def __init__(self, context, request, manager, view):
        while not IProject.providedBy(context):
            context = context.__parent__
            if context is None:
                raise TypeError('Project context is required.')

        super(ProjectOverviewPortlet, self).__init__(
            context, request, manager, view)

    def getContentSchema(self):
        return IContentSchema(self.context)

    def getProjectInfo(self):
        context = self.context

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

    @cache('portlet.projectoverview', ContextModified)
    def updateAndRender(self):
        return super(ProjectOverviewPortlet, self).updateAndRender()
