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
from zope.component import getUtility
from zope.proxy import removeAllProxies
from zope.traversing import api
from zope.schema.fieldproperty import FieldProperty
from zope.lifecycleevent import ObjectModifiedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.app.component.hooks import getSite
from zope.app.intid.interfaces import IIntIds

from zojax.catalog.interfaces import ICatalog
from zojax.members.interfaces import IMembersAware
from zojax.assignment.interfaces import IAssigneesProvider
from zojax.content.type.item import PersistentItem
from zojax.content.type.container import ContentContainer
from zojax.content.type.interfaces import ISearchableContent
from zojax.content.space.workspace import WorkspaceFactory
from zojax.content.type.interfaces import IDraftedContent
from zojax.content.type.searchable import ContentSearchableText
from zojax.permissionsmap.interfaces import IObjectPermissionsMapsManager

from interfaces import _, StateChangedEvent
from interfaces import IProject, IState, ITaskAttributesConfig
from interfaces import IMilestone, IMilestones, IMilestonesFactory


class Milestone(PersistentItem):
    interface.implements(IMilestone, IState)

    state = FieldProperty(IState['state'])

    def reopenTask(self):
        self.state = 1
        event.notify(StateChangedEvent(self, 1))

    def completeTask(self):
        results = getUtility(ICatalog).searchResults(
            type={'any_of': ('project.task',),},
            projectTaskState = {'any_of': (1,)},
            projectTaskMilestone = {'any_of': (getUtility(IIntIds).getId(self),)},
            searchContext = self.__parent__.__parent__)

        for task in results:
            removeAllProxies(task).completeTask()
            event.notify(ObjectModifiedEvent(task))

        self.state = 2
        event.notify(StateChangedEvent(self, 2))


class Milestones(ContentContainer):
    interface.implements(IMilestones)

    showactive = FieldProperty(IMilestones['showactive'])
    showcompleted = FieldProperty(IMilestones['showcompleted'])


class MilestonesWorkspaceFactory(WorkspaceFactory):
    component.adapts(IProject)
    interface.implements(IMilestonesFactory)

    name = 'milestones'
    weight = 210
    title = _(u'Milestones')
    description = _(u'Project milestones.')

    factory = Milestones


@component.adapter(IMilestone)
@interface.implementer(ITaskAttributesConfig)
def taskAttributesConfig(context):
    while not IProject.providedBy(context):
        context = context.__parent__
        if context is None:
            return

    return removeAllProxies(context.get('tasks'))


class MilestoneAssigneesProvider(object):
    component.adapts(IMilestone)
    interface.implements(IAssigneesProvider)

    def __init__(self, milestone):
        self.milestone = milestone

    def assignees(self):
        milestone = self.milestone

        if IDraftedContent.providedBy(milestone):
            milestones = milestone.__parent__.getLocation()
            if milestones is None:
                return []
            project = milestones.__parent__
        else:
            project = milestone.__parent__.__parent__

        group = IMembersAware(project, None)
        if group is None:
            return []

        return removeAllProxies(group.members).keys()


@component.adapter(IMilestone, IObjectModifiedEvent)
def milestoneModified(milestone, ev):
    if milestone.state == 1:
        name = u'project.milestone.active'
    else:
        name = u'project.milestone.completed'

    IObjectPermissionsMapsManager(removeAllProxies(milestone)).set((name,))


@component.adapter(IMilestone)
@interface.implementer(ISearchableContent)
def milestoneSearchable(milestone):
    return api.traverse(getSite(), api.getPath(removeAllProxies(milestone)))


class MilestoneSearchableText(ContentSearchableText):
    component.adapts(IMilestone)

    def getSearchableText(self):
        item = self.content
        title = item.title.strip()
        description = item.description.strip()
        return  u' '.join([s for s in [title, description] if s])
