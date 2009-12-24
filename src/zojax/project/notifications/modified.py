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
from zope.schema.interfaces import IChoice, ICollection, IDate, IDatetime
from zojax.formatter.utils import getFormatter

from templates import TaskNotification


class TaskModifiedTemplate(TaskNotification):

    def update(self):
        super(TaskModifiedTemplate, self).update()

        task = self.context
        ev = self.context0
        request = self.request

        data = {}
        attributes = dict([(attr.interface, list(attr.attributes)) \
                               for attr in ev.descriptions])
        for iface, fields in attributes.items():
            ob = iface(task)
            for fieldId in fields:
                field = iface[fieldId].bind(ob)
                value = field.get(ob)

                if IChoice.providedBy(field):
                    try:
                        value = field.vocabulary.getTerm(value).title
                    except LookupError:
                        pass

                if ICollection.providedBy(field) and \
                        IChoice.providedBy(field.value_type):
                    voc = field.value_type.vocabulary
                    value = u', '.join(
                        [voc.getTerm(v).title for v in value])

                if IDate.providedBy(field):
                    value = getFormatter(request, 'date', 'full').format(value)

                if IDatetime.providedBy(field):
                    value = getFormatter(
                        request, 'dateTime', 'medium').format(value)

                data[field.title] = value

        data = data.items()
        data.sort()
        self.data = data

    @property
    def subject(self):
        return u'%s: Task modified "%s"'%(
            self.project.title, self.context.title)
