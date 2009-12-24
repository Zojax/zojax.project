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
from zope import interface, component, event
from zope.lifecycleevent import ObjectCreatedEvent
from zope.security.proxy import removeSecurityProxy
from zope.schema.fieldproperty import FieldProperty

from zojax.groups.interfaces import IGroup
from zojax.content.type.container import ContentContainer
from zojax.content.space.workspace import WorkspaceFactory
from zojax.content.space.interfaces import IContentSpace, IRootSpace

from interfaces import _, IProjects, IStandaloneProjects, IProjectsFactory


class ProjectsWorkspace(ContentContainer):
    interface.implements(IProjects)

    pagecount = FieldProperty(IProjects['pagecount'])


class StandaloneProjectsWorkspace(ContentContainer):
    interface.implements(IStandaloneProjects)

    browse = FieldProperty(IStandaloneProjects['browse'])
    pagecount = FieldProperty(IStandaloneProjects['pagecount'])


class GroupProjectsWorkspaceFactory(WorkspaceFactory):
    component.adapts(IGroup)
    interface.implements(IProjectsFactory)

    name = u'projects'
    weight = 99999
    description = _(u'Projects container.')

    factory = ProjectsWorkspace

    @property
    def title(self):
        if self.isInstalled():
            return self.space['projects'].title
        else:
            return _(u'Projects')


class StandaloneProjectsWorkspaceFactory(WorkspaceFactory):
    component.adapts(IContentSpace)
    interface.implements(IProjectsFactory)

    name = u'projects'
    weight = 99999
    description = _(u'Projects container.')

    factory = StandaloneProjectsWorkspace

    @property
    def title(self):
        if self.isInstalled():
            return self.space['projects'].title
        else:
            return _(u'Projects')

    def install(self):
        ws = self.space.get(self.name)

        if ws is None:
            ws = self.factory(title = self.title)
            event.notify(ObjectCreatedEvent(ws))
            removeSecurityProxy(self.space)[self.name] = ws

            projects = self.space.get(self.name)
            if IRootSpace.providedBy(self.space):
                projects.browse = True

        return ws
