"""

$Id$
"""
from zope import interface, component
from zope.app.security.settings import Allow, Unset, Deny
from zope.security.proxy import removeSecurityProxy
from zope.securitypolicy.interfaces import IPrincipalRoleMap
from zojax.quick.contenttypes.browser.members import TopRole
from interfaces import IProject


class ProjectsMembersRoles(object):
    component.adapts(IProject)
    interface.implements(IPrincipalRoleMap)

    def __init__(self, context):
        self.context = context
        self.members = context.members

    def getPrincipalsForRole(self, role_id):
        members = {}
        print 'getPrincipalsForRole'
        #        if role_id == 'report.LevelReader':
        #            return [(member, Allow) for member in self.getMembersWithRole(members, MEMBER_ACCESS_READ).keys()]
        #        elif role_id == 'report.LevelWriter':
        #            return [(member, Allow) for member in self.getMembersWithRole(members, MEMBER_ACCESS_WRITE).keys()]
        #        elif role_id == 'report.TopLevelWriter':
        #            if self.context.title != 'Top level':
        #                top_level = removeSecurityProxy(self.context.report.topLevel)
        #            else:
        #                top_level = self.context
        #            for member in top_level.members:
        #                if top_level.members[member].permission == MEMBER_ACCESS_WRITE:
        #                    members[member] = 1
        #            return [(member, Allow) for member in members.keys()]
        return ()



    def getRolesForPrincipal(self, member):
        roles = {'group.Member': 0, 'group.Manager': 0}
        if member in self.members:
            roles['group.Member'] = 1
            if member not in getattr(self.members, 'managers', []):
                roles['group.Manager'] = 0
                print 'Manager = 0'
            else:
                roles['group.Manager'] = 1
                print 'ahaha Manager =1'

        return [(role, value and Allow or Deny) for role, value in roles.items()]

    def getSetting(self, role_id, member):
        return Unset

    def getPrincipalsAndRoles(self):
        print 'getPrincipalsAndRoles'
        pass

