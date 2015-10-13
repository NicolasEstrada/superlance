#!/usr/bin/env python
##############################################################################
#
# Copyright (c) 2007 Agendaless Consulting and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################

# A event listener meant to be subscribed to PROCESS_STATE_CHANGE
# events.  It will send mail when processes that are children of
# supervisord transition unexpectedly to the STOPPED state.

# A supervisor config snippet that tells supervisor to use this script
# as a listener is below.
#
# [eventlistener:stopmailbatch]
# command=python stopmailbatch --toEmail=you@bar.com --fromEmail=me@bar.com
# events=PROCESS_STATE,TICK_60

doc = """\
stopmailbatch.py [--interval=<batch interval in minutes>]
        [--toEmail=<email address>]
        [--fromEmail=<email address>]
        [--subject=<email subject>]
        [--smtpHost=<hostname or address>]

Options:

--interval  - batch cycle length (in minutes).  The default is 1.0 minute.
                  This means that all events in each cycle are batched together
                  and sent as a single email

--toEmail   - the email address to send alerts to

--fromEmail - the email address to send alerts from

--subject   - the email subject line

--smtpHost  - the SMTP server's hostname or address (defaults to 'localhost')

A sample invocation:

stopmailbatch.py --toEmail="you@bar.com" --fromEmail="me@bar.com"

"""

from supervisor import childutils
from superlance.process_state_email_monitor import ProcessStateEmailMonitor


class StopMailBatch(ProcessStateEmailMonitor):

    process_state_events = ['PROCESS_STATE_STOPPING', 'PROCESS_STATE_STOPPED', 'PROCESS_STATE_UNKNOWN']
    output_logs = {
        'PROCESS_STATE_STOPPING': 'Process {groupname}:{processname} (pid {pid}) stopping',
        'PROCESS_STATE_STOPPED': 'Process {groupname}:{processname} (pid {pid}) stopped',
        'PROCESS_STATE_UNKNOWN': 'Process {groupname}:{processname} (pid {pid}) unknown'
    }

    def __init__(self, **kwargs):
        kwargs['subject'] = kwargs.get('subject',
                                       'Stop alert from supervisord')

        ProcessStateEmailMonitor.__init__(self, **kwargs)
        self.now = kwargs.get('now', None)

    def get_process_state_change_msg(self, headers, payload):
        pheaders, pdata = childutils.eventdata(payload + '\n')

        return '{0} -- {1}'.format(
            childutils.get_asctime(self.now), 
            self.output_logs[headers['eventname']].format(**pheaders))


def main():
    stop = StopMailBatch.create_from_cmd_line()
    stop.run()


if __name__ == '__main__':
    main()
