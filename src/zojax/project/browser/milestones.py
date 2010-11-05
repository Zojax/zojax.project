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
from datetime import date
from zope.component import getUtility, getMultiAdapter
from zope.proxy import removeAllProxies
from zope.app.intid.interfaces import IIntIds
from zope.traversing.browser import absoluteURL
from zope.dublincore.interfaces import IDCTimes
from zope.contentprovider.interfaces import IContentProvider

from zojax.formatter.utils import getFormatter
from zojax.catalog.interfaces import ICatalog
from zojax.ownership.interfaces import IOwnership
from zojax.principal.profile.interfaces import IPersonalProfile

from zojax.project.interfaces import _


class BrowseMilestones(object):

    def listMilestones(self):
        request = self.request
        context = self.context

        today = date.today()
        ids = getUtility(IIntIds)
        catalog = getUtility(ICatalog)
        formatter = getFormatter(request, 'fancyDatetime', 'medium')
        dateFormatter = getFormatter(request, 'date', 'full')

        milestones = []
        active_milestones = []

        for ms in context.values():
            dc = IDCTimes(ms)

            principal = IOwnership(ms).owner
            profile = IPersonalProfile(principal, None)

            space = getattr(profile, 'space', None)
            if space is not None:
                space = u'%s/'%absoluteURL(space, request)

            tasks = getMultiAdapter(
                (ms, request, self),
                IContentProvider, 'project.tasks.browseactive')
            tasks.update()

            info = {
                'name': ms.__name__,
                'title': ms.title,
                'creator': getattr(profile, 'title', None),
                'space': space,
                'created': formatter.format(dc.created),
                'date': dateFormatter.format(ms.date),
                'tasks': None,
                'completed': None,
                'overdue': None,
                'percent': 100,
                'milestone': ms
                }

            if context.showactive:
                info['tasks'] = tasks

            if context.showcompleted:
                info['completedtasks'] = getMultiAdapter(
                    (ms, request, self),
                    IContentProvider, 'project.tasks.browsecompleted')
                info['completedtasks'].update()

            # date
            if ms.state == 1 and ms.date < today:
                info['overdue'] = today - ms.date

            # tasks statistics
            completed = len(catalog.searchResults(
                type={'any_of': ('project.task',),},
                projectTaskState = {'any_of': (2,)},
                projectTaskMilestone = {
                        'any_of': (ids.getId((removeAllProxies(ms))),)},
                searchContext = context.__parent__.__parent__,
                noPublishing=True, noSecurityChecks=True))

            total = len(tasks.dataset) + completed
            info['total'] = total
            info['completed'] = completed
            if total > 0:
                info['percent'] = int(completed/(total/100.0))
            
            if info['percent'] < 100:    
                active_milestones.append((ms.date, ms.title, info))
            else:
                milestones.append((ms.date, ms.title, info))
        milestones.sort()
        active_milestones.sort()
        return [info for _d, _t, info in active_milestones], [info for _d, _t, info in milestones]
