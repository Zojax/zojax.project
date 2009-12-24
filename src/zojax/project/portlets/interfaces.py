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
from zope import schema, interface
from zojax.portlet.interfaces import _ as pMsg
from zojax.portlet.interfaces import \
    IPortletManagerWithStatus, ENABLED, statusVocabulary
from zojax.project.interfaces import _


class IProjectsRightPortletManager(IPortletManagerWithStatus):

    portletIds = schema.Tuple(
        title = pMsg('Portlets'),
        value_type = schema.Choice(vocabulary = 'zojax portlets'),
        default = ('portlet.actions','portlet.activity',),
        required = True)

    status = schema.Choice(
        title = pMsg(u'Status'),
        vocabulary = statusVocabulary,
        default = ENABLED,
        required = True)


class IProjectsLeftPortletManager(IPortletManagerWithStatus):

    portletIds = schema.Tuple(
        title = pMsg('Portlets'),
        value_type = schema.Choice(vocabulary = 'zojax portlets'),
        default = (),
        required = True)

    status = schema.Choice(
        title = pMsg(u'Status'),
        vocabulary = statusVocabulary,
        default = ENABLED,
        required = True)


class IProjectRightPortletManager(IPortletManagerWithStatus):

    portletIds = schema.Tuple(
        title = pMsg('Portlets'),
        value_type = schema.Choice(vocabulary = 'zojax portlets'),
        default = ('portlet.actions',
                   'portlet.comments',),
        required = True)

    status = schema.Choice(
        title = pMsg(u'Status'),
        vocabulary = statusVocabulary,
        default = ENABLED,
        required = True)


class IProjectLeftPortletManager(IPortletManagerWithStatus):

    portletIds = schema.Tuple(
        title = pMsg('Portlets'),
        value_type = schema.Choice(vocabulary = 'zojax portlets'),
        default = (),
        required = True)

    status = schema.Choice(
        title = pMsg(u'Status'),
        vocabulary = statusVocabulary,
        default = ENABLED,
        required = True)


class IProjectContentPortletManager(IPortletManagerWithStatus):

    portletIds = schema.Tuple(
        title = pMsg('Portlets'),
        value_type = schema.Choice(vocabulary = 'zojax portlets'),
        default = ('portlet.projectoverview',),
        required = True)

    status = schema.Choice(
        title = pMsg(u'Status'),
        vocabulary = statusVocabulary,
        default = ENABLED,
        required = True)


class IProjectSearchPortlet(interface.Interface):
    """ group search portlet """


class IProjectOverviewPortlet(interface.Interface):
    """ project overview portlet """


class IProjectOverviewContentPortlet(interface.Interface):
    """ project overview portlet """

    showLogo = schema.Bool(
        title = _('Show project logo'),
        default = True,
        required = True)


class IProjectsPortletSettings(interface.Interface):

    label = schema.TextLine(
        title = _('Label'),
        required = False)

    number = schema.Int(
        title = _(u'Number of items'),
        description = _(u'Number of items to display'),
        default = 7,
        required = True)


class IProjectsPortlet(IProjectsPortletSettings):
    """ projects portlet """


class IProjectsContentPortlet(IProjectsPortletSettings):
    """ projects content portlet """

    showLogo = schema.Bool(
        title = _('Show project logo'),
        default = True,
        required = True)
