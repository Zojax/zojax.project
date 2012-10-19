from zope import interface, component
from zope.component import getUtility
from zope.securitypolicy.interfaces import IRolePermissionMap

from zojax.permissionsmap.interfaces import IPermissionsMap
from interfaces import IProject

@component.adapter(IProject)
@interface.implementer(IRolePermissionMap)
def getContentPermissions(context):
    if context.ptype == 'open':
        return getUtility(IPermissionsMap, 'project.open')
    elif context.ptype == 'members':
        return getUtility(IPermissionsMap, 'project.members')
    elif context.ptype == 'private':
        return getUtility(IPermissionsMap, 'project.private')
    else:
        return getUtility(IPermissionsMap, 'project.secret')