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
from zope.component import getUtility, queryMultiAdapter
from zope.security.proxy import removeSecurityProxy
from zope.copypastemove.interfaces import IObjectCopier
from zope.app.intid.interfaces import IIntIds
from zope.lifecycleevent import ObjectCreatedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.schema.fieldproperty import FieldProperty

from zojax.richtext.field import RichTextProperty
from zojax.filefield.field import FileFieldProperty
from zojax.members.interfaces import IMembersAware
from zojax.content.type.container import ContentContainer
from zojax.content.type.searchable import ContentSearchableText
from zojax.content.permissions.utils import updatePermissions
from zojax.content.space.interfaces import IWorkspacesManagement
from zojax.permissionsmap.interfaces import IObjectPermissionsMapsManager

from interfaces import IProject, IStandaloneProject
from interfaces import StateChangedEvent


class Project(ContentContainer):
    interface.implements(IProject, IWorkspacesManagement)

    showTabs = True
    showHeader = True
    workspaces = ('overview', 'tasks', 'milestones')
    enabledWorkspaces = ()
    defaultWorkspace = 'overview'
    ptype = 'open'

    logo = FileFieldProperty(IProject['logo'])
    text = RichTextProperty(IProject['text'])
    startDate = FieldProperty(IProject['startDate'])
    endDate = FieldProperty(IProject['endDate'])
    state = FieldProperty(IProject['state'])

    @property
    def id(self):
        return getUtility(IIntIds).getId(self)

    def isEnabled(self, workspaceFactory):
        return workspaceFactory.isAvailable() and \
            workspaceFactory.name in self.workspaces

    def reopenProject(self):
        """ reopen Project
        """
        self.state = 1
        event.notify(StateChangedEvent(self, 1))

    def completeProject(self):
        """ complete Project
        """
        self.state = 2
        event.notify(StateChangedEvent(self, 2))

class StandaloneProject(Project):
    interface.implements(IStandaloneProject, IMembersAware)

    workspaces = ('overview', 'members', 'tasks', 'milestones')

    @property
    def members(self):
        return self.get('members')

    def isEnabled(self, workspaceFactory):
        if workspaceFactory.name == 'members':
            return True

        return workspaceFactory.isAvailable() and \
            workspaceFactory.name in self.workspaces


@component.adapter(IProject, IObjectModifiedEvent)
def projectModified(project, ev):
    if not project.ptype:
        project.ptype = u'open'

    IObjectPermissionsMapsManager(
        removeSecurityProxy(project)).set(('project.%s'%project.ptype,))

    updatePermissions(project)


@component.adapter(IProject)
@interface.implementer(IMembersAware)
def projectMembers(project):
    while not IMembersAware.providedBy(project) and project is not None:
        project = project.__parent__

    return project


class ProjectSearchableText(ContentSearchableText):
    component.adapts(IProject)

    def getSearchableText(self):
        text = super(ProjectSearchableText, self).getSearchableText()

        try:
            return text + u' ' + self.content.text.text
        except AttributeError:
            return text


class ProjectCopier(object):
    component.adapts(IProject)
    interface.implements(IObjectCopier)

    def __init__(self, object):
        self.context = object

    def copyTo(self, target, new_name=None):
        raise RuntimeError('Object is not copyable')

    def copyable(self):
        return False

    def copyableTo(self, target, name=None):
        return False
