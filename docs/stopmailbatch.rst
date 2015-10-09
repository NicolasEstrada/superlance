:command:`stopmailbatch` Documentation
=======================================

:command:`stopmailbatch` is a supervisor "event listener", intended to be
subscribed to ``PROCESS_STATE`` and ``TICK_60`` events.  It monitors
all processes running under a given supervisord instance.

Similar to :command:`crashmailbatch`, :command:`stopmailbatch` sends email alerts 
generated within the configured time interval are batched together to avoid 
sending too many emails. The differnce is that this it's send them for
``PROCESS_STATE_STOPPED``, ``PROCESS_STATE_STOPPING`` and ``PROCESS_STATE_UNKNOWN``.

:command:`stopmailbatch` is a "console script" installed when you install
:mod:`superlance`.  Although :command:`stopmailbatch` is an executable 
program, it isn't useful as a general-purpose script:  it must be run as a
:command:`supervisor` event listener to do anything useful.

Command-Line Syntax
-------------------

.. code-block:: sh

   $ stopmailbatch --toEmail=<email address> --fromEmail=<email address> \
           [--interval=<batch interval in minutes>] [--subject=<email subject>] \
		   [--tickEvent=<event name>]
   
.. program:: stopmailbatch

.. cmdoption:: -t <destination email>, --toEmail=<destination email>
   
   Specify an email address to which stop notification messages are sent.
 
.. cmdoption:: -f <source email>, --fromEmail=<source email>
   
   Specify an email address from which stop notification messages are sent.

.. cmdoption:: -i <interval>, --interval=<interval>
   
   Specify the time interval in minutes to use for batching notifcations.
   Defaults to 1.0 minute.

.. cmdoption:: -s <email subject>, --subject=<email subject>
   
   Override the email subject line.  Defaults to "stop alert from supervisord"

.. cmdoption:: -e <event name>, --tickEvent=<event name>

   Override the TICK event name.  Defaults to "TICK_60"

Configuring :command:`stopmailbatch` Into the Supervisor Config
----------------------------------------------------------------

An ``[eventlistener:x]`` section must be placed in :file:`supervisord.conf`
in order for :command:`stopmailbatch` to do its work. See the "Events" chapter in
the Supervisor manual for more information about event listeners.

The following example assumes that :command:`stopmailbatch` is on your system
:envvar:`PATH`.

.. code-block:: ini

   [eventlistener:stopmailbatch]
   command=stopmailbatch --toEmail="alertme@fubar.com" --fromEmail="supervisord@fubar.com" 
   events=PROCESS_STATE,TICK_60
