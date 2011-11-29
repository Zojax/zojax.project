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
from zojax.table.interfaces import ITable
from zojax.pageelement.interfaces import IPageElement
from zojax.content.actions.interfaces import IAction
from zojax.content.actions.interfaces import IAddContentCategory
from zojax.content.actions.interfaces import IManageContentCategory


class ITasksTable(ITable):
    """ tasks table """


class IComplatedTasksTable(ITasksTable):
    """ completed tasks """


class IMilestoneTasksTable(ITasksTable):
    """ tasks table """


class IAddCategoryAction(IAction, IAddContentCategory):
    """ add category action """


class IManageCategoriesAction(IAction, IManageContentCategory):
    """ manage categories action """


class ICompleteTaskAction(IAction, IManageContentCategory):
    """ complete task action """


class IReopenTaskAction(IAction, IManageContentCategory):
    """ reopen task action """


class ICompleteProjectAction(IAction, IManageContentCategory):
    """ complete project action """


class IReopenProjectAction(IAction, IManageContentCategory):
    """ reopen project action """


class IUploadAttachmentsAction(IAction, IManageContentCategory):
    """ upload attachments """


class IAddTaskAction(IAction, IAddContentCategory):
    """ add task action """


class IAddMilestoneAction(IAction, IAddContentCategory):
    """ add milestone action """


class ICommentsView(interface.Interface):
    """ comments view """


class IAttachmentsView(interface.Interface):
    """ attachments view """


class ITaskFooter(IPageElement):
    """ task footer """


class ITaskInformation(IPageElement):
    """ task information """


class IMilestoneInformation(IPageElement):
    """ milestone information """


class IMilestonesInformation(IPageElement):
    """ milestone information """


class IProjectInformation(IPageElement):
    """ project information """


class IProjectsInformation(IPageElement):
    """ project information """
