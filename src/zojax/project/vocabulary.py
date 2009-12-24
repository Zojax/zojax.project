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
from zope.component import getUtility
from zope.proxy import removeAllProxies
from zope.i18nmessageid import MessageFactory
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.app.intid.interfaces import IIntIds
from zojax.catalog.interfaces import ICatalog
from zojax.content.draft.interfaces import IDraftContent

import interfaces

_ = MessageFactory('zojax.project')

emptyVoc = SimpleVocabulary(())

stateVocabulary = SimpleVocabulary((
        SimpleTerm(1, '1', _(u'Open')),
        SimpleTerm(2, '2', _(u'Completed')),
        ))

priorityVocabulary = SimpleVocabulary((
        SimpleTerm(1, '1', _(u'Highest')),
        SimpleTerm(2, '2', _(u'High')),
        SimpleTerm(3, '3', _(u'Medium')),
        SimpleTerm(4, '4', _(u'Low'))))


class SeverityVocabulary(object):
    interface.implements(IVocabularyFactory)

    def __call__(self, context):
        config = interfaces.ITaskAttributesConfig(
            removeAllProxies(context), None)
        if config is not None:
            return SimpleVocabulary(
                [SimpleTerm(v,v,v) for v in config.severity])
        else:
            return emptyVoc


class StatusVocabulary(object):
    interface.implements(IVocabularyFactory)

    def __call__(self, context):
        config = interfaces.ITaskAttributesConfig(
            removeAllProxies(context), None)
        if config is not None:
            return SimpleVocabulary(
                [SimpleTerm(v,v,v) for v in config.status])
        else:
            return emptyVoc


def ActiveMilestonesVocabulary(context):
    while True:
        if interfaces.IProject.providedBy(context):
            break

        if IDraftContent.providedBy(context):
            context = context.getLocation()
            if not interfaces.ITasks.providedBy(context):
                context = None
            context = getattr(context, '__parent__', None)
            break

        context = getattr(context, '__parent__', None)
        if context is None:
            break

    if context is None:
        return emptyVoc

    mst = context.get('milestones')
    if mst is None:
        return emptyVoc

    ids = getUtility(IIntIds)

    milestones = []
    for milestone in mst.values():
        id = ids.getId(removeAllProxies(milestone))
        milestones.append(
            (milestone.title, SimpleTerm(id, str(id), milestone.title)))

    milestones.sort()
    return SimpleVocabulary([term for _t, term in milestones])
