import unittest
import mock
from superlance.compat import StringIO

class StopMailBatchTests(unittest.TestCase):
    from_email = 'testFrom@blah.com'
    to_emails = ('testTo@blah.com')
    subject = 'Test Alert'
    unexpected_err_msg = 'Process bar:foo (pid 58597) stopped'

    def _get_target_class(self):
        from superlance.stopmailbatch import stopMailBatch
        return StopMailBatch

    def _make_one_mocked(self, **kwargs):
        kwargs['stdin'] = StringIO()
        kwargs['stdout'] = StringIO()
        kwargs['stderr'] = StringIO()
        kwargs['from_email'] = kwargs.get('from_email', self.from_email)
        kwargs['to_emails'] = kwargs.get('to_emails', self.to_emails)
        kwargs['subject'] = kwargs.get('subject', self.subject)

        obj = self._get_target_class()(**kwargs)
        obj.send_email = mock.Mock()
        return obj

    def get_process_stopped_event(self, pname, gname, expected):
        headers = {
            'ver': '3.0', 'poolserial': '7', 'len': '71',
            'server': 'supervisor', 'eventname': 'PROCESS_STATE_STOPPED',
            'serial': '7', 'pool': 'checkmailbatch',
        }
        payload = 'processname:%s groupname:%s from_state:RUNNING expected:%d \
pid:58597' % (pname, gname, expected)
        return (headers, payload)

    def test_get_process_state_change_msg_expected(self):
        stop = self._make_one_mocked()
        hdrs, payload = self.get_process_stopped_event('foo', 'bar', 1)
        self.assertEqual(None, stop.get_process_state_change_msg(hdrs, payload))

    def test_get_process_state_change_msg_unexpected(self):
        stop = self._make_one_mocked()
        hdrs, payload = self.get_process_stopped_event('foo', 'bar', 0)
        msg = stop.get_process_state_change_msg(hdrs, payload)
        self.assertTrue(self.unexpected_err_msg in msg)

    def test_handle_event_exit_expected(self):
        stop = self._make_one_mocked()
        hdrs, payload = self.get_process_stopped_event('foo', 'bar', 1)
        stop.handle_event(hdrs, payload)
        self.assertEqual([], stop.get_batch_msgs())
        self.assertEqual('', stop.stderr.getvalue())

    def test_handle_event_exit_unexpected(self):
        stop = self._make_one_mocked()
        hdrs, payload = self.get_process_stopped_event('foo', 'bar', 0)
        stop.handle_event(hdrs, payload)
        msgs = stop.get_batch_msgs()
        self.assertEqual(1, len(msgs))
        self.assertTrue(self.unexpected_err_msg in msgs[0])
        self.assertTrue(self.unexpected_err_msg in stop.stderr.getvalue())

if __name__ == '__main__':
    unittest.main()
