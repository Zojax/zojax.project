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
""" Default Project Task workflow

$Id$
"""
from zojax.workflow import State, NullState, Workflow
from zojax.workflow import ManualTransition, AutomaticTransition


s_pending = State(
    'pending', 'Pending',
    permissionsmap='zojax.project.task.pending')

s_accepted = State(
    'accepted', 'Accepted',
    permissionsmap='zojax.project.task.accepted')

s_approving = State(
    'approving', 'Approving',
    permissionsmap='zojax.project.task.approving')

s_inprocess = State(
    'in-process', 'In-Process',
    permissionsmap='zojax.project.task.in-process')

s_deferred = State(
    'deferred', 'Deferred',
    permissionsmap='zojax.project.task.deferred')

s_onhold = State(
    'on-hold', 'On-Hold',
    permissionsmap='zojax.project.task.on-hold')

s_rework = State(
    'rework', 'Rework',
    permissionsmap='zojax.project.task.rework')

s_testing = State(
    'testing', 'Testing',
    permissionsmap='zojax.project.task.testing')

s_approved = State(
    'approved', 'Approved',
    permissionsmap='zojax.project.task.approved')

s_waitdata = State(
    'waiting-data', 'Waiting-Data',
    permissionsmap='zojax.project.task.waiting-data')

s_rejected = State(
    'rejected', 'Rejected',
    permissionsmap='zojax.project.task.rejected')

s_released = State(
    'released', 'Released',
    permissionsmap='zojax.project.task.released')


init = AutomaticTransition(
    'init', 'Init workflow', (NullState,), s_pending)

accept = ManualTransition(
    'accept', 'Accept task', (s_pending, s_approving, s_deferred),
    s_accepted, permission='zojax.project.workflow.Accept')

reject = ManualTransition(
    'reject', 'Reject task',
    (s_pending, s_accepted, s_approving, s_inprocess,
     s_onhold, s_rework, s_deferred), s_rejected,
    permission='zojax.project.workflow.Reject')

start = ManualTransition(
    'start', 'Start work', (s_accepted, s_approved), s_inprocess,
    permission='zojax.project.workflow.Start')

restart = ManualTransition(
    'restart', 'Restart', (s_onhold, s_rework, s_waitdata), s_inprocess,
    permission='zojax.project.workflow.Restart')

reaccept = ManualTransition(
    'reaccept', 'Reaccept', (s_rejected, s_released), s_accepted,
    permission='zojax.project.workflow.Accept')

waitdata = ManualTransition(
    'waitdata', 'Wait customer data', (s_accepted, s_approved, s_inprocess),
    s_waitdata, permission='zojax.project.workflow.WaitData')

approving = ManualTransition(
    'approving', 'Client approving', (s_pending, s_accepted), s_approving,
    permission='zojax.project.workflow.Approving')

approve = ManualTransition(
    'approve', 'Approve task', (s_approved,), s_approved,
    permission='zojax.project.workflow.Approve')

release = ManualTransition(
    'release', 'Release',
    (s_pending, s_accepted, s_approved, s_inprocess, s_rework, s_testing),
    s_released, permission='zojax.project.workflow.Release')

test = ManualTransition(
    'test', 'Test', (s_inprocess, s_rework), s_testing,
    permission='zojax.project.workflow.Test')

deferred = ManualTransition(
    'deferred', 'Deferred', (s_pending, s_accepted,
                             s_rejected, s_inprocess, s_onhold),
    s_deferred, permission='zojax.project.workflow.Deferred')

rework = ManualTransition(
    'rework', 'Rework', (s_testing,), s_rework,
    permission='zojax.project.workflow.Rework')

hold = ManualTransition(
    'hold', 'Hold on ticket', (s_accepted, s_approved, s_inprocess), s_onhold,
    permission='zojax.project.workflow.Hold')


defaultWorkflow = Workflow('default', 'Default Task Workflow',
                           [init, accept, reject, start, restart,
                            reaccept, waitdata, approving, approve,
                            release, test, deferred, rework, hold])
