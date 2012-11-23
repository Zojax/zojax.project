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
""" Project interfaces

$Id$
"""
from zope import schema, interface
from zope.i18nmessageid import MessageFactory
from zope.component.interfaces import ObjectEvent, IObjectEvent
from zojax.assignment.field import AssigneesField
from zojax.assignment.interfaces import IAssignmentsAware
from zojax.richtext.field import RichText
from zojax.filefield.field import ImageField
from zojax.widget.list.field import SimpleList
from zojax.widget.radio.field import RadioChoice
from zojax.widget.checkbox.field import CheckboxList
from zojax.content.activity.interfaces import IContentActivityRecord
from zojax.content.type.interfaces import IItem
from zojax.content.space.interfaces import ISpace, IWorkspace, IWorkspaceFactory
from zojax.content.discussion.interfaces import IComment
from zojax.content.feeds.interfaces import IRSS2Feed
from zojax.project import types, vocabulary

_ = MessageFactory('zojax.project')


class IProject(IItem, ISpace):
    """ iternal team info """

    ptype = RadioChoice(
        title = _(u'Project type'),
        description = _(u'Select type for this project.'),
        vocabulary = types.types,
        default = 'open',
        required = False)

    logo = ImageField(
        title = _('Logo'),
        description = _('Project logo'),
        maxWidth = 250, maxHeight = 190, scale = True,
        required = False)

    startDate = schema.Date(
        title = _('Start date'),
        description = _('Project starting date.'),
        required = False)

    endDate = schema.Date(
        title = _('End date'),
        description = _('Project ending date.'),
        required = False)

    text = RichText(
        title = _(u'Text'),
        description = _(u'Project long description.'),
        required = False)


class IStandaloneProject(IProject):
    """ Standalone project """

    members = interface.Attribute('Members')


class IProjects(IItem, IWorkspace):
    """ projects container """

    pagecount = schema.Int(
        title = _('Page count'),
        description = _('Number of projects per page.'),
        default = 15,
        required = True)


class IStandaloneProjects(IProjects):
    """ standalone projects container """

    browse = schema.Bool(
        title = _('Browse all'),
        description = _('Browse projects in all sub spaces.'),
        default = False,
        required = False)


class IProjectsFactory(IWorkspaceFactory):
    """ projects woprkspace factory """


class IProjectProduct(interface.Interface):
    """ project product """

    tasks_active_page_size = schema.Int(
        title = _('Number of active tasks on page.'),
        default = 30)

    tasks_completed_page_size = schema.Int(
        title = _('Number of completed tasks on page.'),
        default = 30)


# project state

class IProjectState(interface.Interface):
    """ project state: open/completed """

    state = schema.Choice(
        title = _('Open/Completed state'),
        vocabulary = vocabulary.stateVocabulary,
        default = 1,
        required = True)

    def reopenProject():
        """ reopen project """

    def completeProject():
        """ complete project """


# task/milestone state

class IState(interface.Interface):
    """ state: open/completed """

    state = schema.Choice(
        title = _('Open/Completed state'),
        vocabulary = vocabulary.stateVocabulary,
        default = 1,
        required = True)

    def reopenTask():
        """ reopne task """

    def completeTask():
        """ complete task """


class IStateActivityRecord(IContentActivityRecord):
    """ activity record """

    state = schema.Choice(
        title = _('Open/Completed state'),
        vocabulary = vocabulary.stateVocabulary,
        default = 1,
        required = True)


class IStateChangedEvent(IObjectEvent):
    """ state changed event """

    state = interface.Attribute('State')


class StateChangedEvent(ObjectEvent):
    interface.implements(IStateChangedEvent)

    def __init__(self, object, state):
        super(StateChangedEvent, self).__init__(object)

        self.state = state


# task/milestone due date

class IDueDate(interface.Interface):
    """ due date """

    date = schema.Date(
        title = _(u'Due date'),
        description = _('Completion date.'),
        required = True)


# task/milestone assignments

class ITaskAssignments(interface.Interface):
    """ assignments """

    assigned = schema.List(
        title = _(u'Assigned to'),
        value_type = schema.Choice(vocabulary = 'zojax.group.members'),
        required = False)


# milestones

class IMilestone(IDueDate, IAssignmentsAware):
    """ project milestone """

    title = schema.TextLine(
        title = _('Title'),
        description = _('Milestone title.'),
        required = True)

    assigned = AssigneesField(
        title = _(u'Assigned to'),
        required = False)

    text = RichText(
        title = _(u'Information'),
        description = _(u'Milestone detailed information.'),
        required = False)


class IAddTasksCustom(IDueDate, IAssignmentsAware):
    """ project milestone """
    title = schema.TextLine(
        title = _('Title'),
        description = _('Tasks Custom title.'),
        required = True)

    assigned = AssigneesField(
        title = _(u'Assigned to'),
        required = False)

    text = RichText(
        title = _(u'Information'),
        description = _(u'Tasks Custom detailed information.'),
        required = False)


class IMilestones(IItem, IWorkspace):
    """ milestones workspace """

    showactive = schema.Bool(
        title = _('Active tasks'),
        description = _('Show active tasks in milestones browsing view.'),
        default = True,
        required = True)

    showcompleted = schema.Bool(
        title = _('Completed tasks'),
        description = _('Show completed tasks in milestones browsing view.'),
        default = True,
        required = True)


class IMilestonesFactory(IWorkspaceFactory):
    """ milestones workspace factory """


# tasks

class ITask(IDueDate, IAssignmentsAware):
    """ project task """

    title = schema.TextLine(
        title = _('Title'),
        description = _('Task title.'),
        required = True)

    milestone = schema.Choice(
        title = _(u'Milestone'),
        description = _(u'Assign task to milestone.'),
        vocabulary = 'project.milestone.active',
        required = False)

    text = RichText(
        title = _(u'Information'),
        description = _(u'Task detailed information.'),
        required = True)


class ITaskAssignee(interface.Interface):
    """ task assignee """

    assigned = AssigneesField(
        title = _(u'Assigned to'),
        required = False)


class ITaskAttributes(interface.Interface):
    """ additional attributes """

    priority = schema.Choice(
        title = _(u'Priority'),
        vocabulary = vocabulary.priorityVocabulary,
        default = 4,
        required = False)

    severity = schema.Choice(
        title = _(u'Severity'),
        description = _(u'Select task severity.'),
        vocabulary = 'project.task.severity',
        required = False)

    category = CheckboxList(
        title = _(u'Category'),
        description = _(u'Select task category.'),
        vocabulary = 'project.task.categories',
        default = [],
        required = False)


class ITaskAttributesConfig(interface.Interface):
    """ additional attributes config """

    severity = SimpleList(
        title = _(u'Severity'),
        description = _(u'Ticket severity.'),
        default = ['blocker', 'critical', 'major',
                   'normal', 'minor', 'trivial', 'enhancement'],
        required = False)


class ITaskCategory(IItem):
    """ Task Category """


class ITaskCategoryContainer(interface.Interface):
    """ Categories container """


class ITasks(IItem, IWorkspace):
    """ tasks workspace """

    category = interface.Attribute('Categories container')


class ITasksFactory(IWorkspaceFactory):
    """ tasks workspace factory """


class ITaskComment(IComment):
    """ task comment """

    changes = interface.Attribute('Task changes')
    attachment = interface.Attribute('Ticket attachments')

    def getAttachments():
        """ return attachments """


class IProjectTasksRSSFeed(IRSS2Feed):
    """ project tasks rss feed """


class ITasksRSSFeed(IRSS2Feed):
    """ tasks rss feed """
