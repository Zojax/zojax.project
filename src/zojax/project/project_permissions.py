from zope import interface, component
from zope.component import getUtility
from zope.securitypolicy.interfaces import IRolePermissionMap

from zojax.permissionsmap.interfaces import IPermissionsMap
from zojax.blogger.interfaces import *
from interfaces import IProject
@component.adapter(IBlog)
@interface.implementer(IRolePermissionMap)
def getContentPermissions(context):
    if IProject.providedBy(context.__parent__):
        if context.__parent__.ptype == 'open':
            return getUtility(IPermissionsMap, 'project.open')
        elif context.__parent__.ptype == 'members':
            return getUtility(IPermissionsMap, 'project.members')
        elif context.__parent__.ptype == 'private':
            return getUtility(IPermissionsMap, 'project.private')
        else:
            return getUtility(IPermissionsMap, 'project.secret')