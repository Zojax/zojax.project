"""

$Id$
"""
from zope import interface, component
from zope.app.security.settings import Allow, Unset, Deny
from zope.securitypolicy.interfaces import IPrincipalRoleMap
from zojax.blogger.interfaces import *

class ProjectsMembersRoles(object):
    component.adapts(IBlog)
    interface.implements(IPrincipalRoleMap)

    def __init__(self, context):
        self.context = context
        try:
            self.ptype = context.__parent__.ptype
        except AttributeError:
            self.ptype = None
        try:
            self.members = context.__parent__.members
        except AttributeError:
            self.members = None

    def getPrincipalsForRole(self, role_id):
        return ()


    def getRolesForPrincipal(self, member):
        roles = {'group.Member': 0, 'group.Manager': 0}
        if self.ptype == 'open' and member == 'zope.Authenticated':
            roles['zope.Authenticated'] = 1
        if self.members:
            if member in self.members:
                roles['group.Member'] = 1
                if member not in getattr(self.members, 'managers', []):
                    roles['group.Manager'] = 0
                else:
                    roles['group.Manager'] = 1
        return [(role, value and Allow or Deny) for role, value in roles.items()]

    def getSetting(self, role_id, member):
        return Unset

    def getPrincipalsAndRoles(self):
        pass
