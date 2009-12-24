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
from zope.component import getUtility
from zope.traversing.browser import absoluteURL
from zope.dublincore.interfaces import IDCTimes
from zope.index.text.parsetree import ParseError

from zojax.batching.batch import Batch
from zojax.catalog.interfaces import ICatalog
from zojax.filefield.interfaces import IImage
from zojax.ownership.interfaces import IOwnership
from zojax.members.interfaces import IMembersAware
from zojax.statusmessage.interfaces import IStatusMessage

from zojax.project.types import types
from zojax.project.interfaces import _, ITask, IStandaloneProjects


class BrowseProjects(object):

    hasGroups = True
    batch = Batch((), 15)

    def update(self):
        context = self.context
        request = self.request

        if IStandaloneProjects.providedBy(context):
            browseAll = context.browse
        else:
            browseAll = False

        if not browseAll:
            self.hasGroups = bool(len(context))
            if not self.hasGroups:
                return

            searchContext = context
        else:
            searchContext = context.__parent__

        if 'form.search.clear' in request:
            self.redirect('./index.html')
            return

        catalog = getUtility(ICatalog)

        if 'form.search' in request:
            s = request.get('form.searchText', u'').strip()
            if s:
                query = {
                    'type': {'any_of': (
                            'content.project','content.standaloneproject')},
                    'isDraft': {'any_of': (False,)},
                    'traversablePath': {'any_of': (searchContext,)},
                    'searchableText': s}

                try:
                    results = catalog.searchResults(**query)
                except ParseError, e:
                    IStatusMessage(request).add(e, 'error')
                    return

                self.batch = Batch(
                    results, size=context.pagecount,
                    context=context, request=request)
            else:
                IStatusMessage(request).add(
                    _('Please enter one or more words for search.'), 'warning')
            return

        results = catalog.searchResults(
            type = {'any_of': ('content.project','content.standaloneproject')},
            isDraft = {'any_of': (False,)},
            traversablePath = {'any_of': (searchContext,)}, sort_on='title')

        if not results:
            self.hasGroups = False
            return

        self.managers = {}
        self.catalog = catalog
        self.batch = Batch(
            results, size = context.pagecount,
            context = context, request = request)

    def getGroupInfo(self, project):
        dc = IDCTimes(project)
        principal = getattr(IOwnership(project, None), 'owner', None)
        request = self.request

        info = {
            'id': id,
            'title': project.title,
            'description': project.description,
            'owner': principal,
            'created': dc.created,
            'members': None,
            'default': not bool(project.logo),
            'type': types.getTerm(project.ptype),
            'managers': [],
            'tasks': None}

        membersaware = IMembersAware(project, None)
        if membersaware is not None:
            members = membersaware.members

            info['members'] = len(members)
            info['membersURL'] = u'%s/'%absoluteURL(members, request)

            managers = []
            for mid in members.managers:
                managerinfo = self.managers.get(mid)
                if managerinfo is None:
                    member = members[mid]
                    managerinfo = {'title': member.profile.title, 'space': ''}

                    space = member.space
                    if space is not None:
                        managerinfo['space'] = u'%s/'%absoluteURL(space, request)

                    self.managers[mid] = managerinfo

                managers.append((managerinfo['title'], managerinfo))

            managers.sort()
            info['managers'] = [m for r, m in managers]

        if u'tasks' in project:
            tasks = project['tasks']

            total = len(tasks)-1

            if total>0:
                tasks = self.catalog.searchResults(
                    type = {'any_of': ('project.task',)},
                    projectTaskState = {'any_of': (2,)},
                    searchContext = project,
                    noSecurityChecks = True, noPublishing = True)
                completed = len(tasks)
                info['tasks'] = (total, completed, int(completed/(total/100.0)))
            else:
                completed = 0
                info['tasks'] = (0, 0, '0')

        return info
