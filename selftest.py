import os
import unittest
import system
import configuration
import logmodule

class TestSystem(unittest.TestCase):
    def test_isfloat(self):
        logmodule.logger.debug('Start unittest system.py func - is_float')
        l = [{'var': int(1), 'result': True}, {'var': str(1), 'result': True}, {'var': float(1), 'result': True},
             {'var': bytes(1), 'result': False}, {'var': str('abc'), 'result': False}, {'var': str('a'), 'result': False}]
        for i in l:
            if i['result']:
                self.assertTrue(system.isfloat(i['var']), msg='Fail in {0} as type {1}'.format(i['var'], type(i['var'])))
            else:
                self.assertFalse(system.isfloat(i['var']), msg='Unexpected <True> in {0} as type {1}'.format(i['var'],
                                                                                                             type(i['var'])))
        logmodule.logger.debug('Done')

    def test_error_log_write(self):
        logmodule.logger.debug('Start unittest system.py func - error_log_write')
        l = [{'mess': 'Test func', 'trace': 'Test trace'}, {'mess': 'Test func', 'trace': None}]
        for i in l:
            system.error_log_write(i['mess'], i['trace'])
            self.assertTrue(os.path.exists('error.log'), msg='Do not create a log file')
            x = [i.replace('Error string', '').replace(' ', '').replace('\n', '') for i in open('error.log', 'r')]
            if i['mess']:
                self.assertIn(i['mess'].replace(' ', ''), x,  msg='Do not write message in file')
            if i['trace']:
                self.assertIn(i['trace'].replace(' ', ''), x, msg='Do not write trace in file')
            if not i['mess'] and not i['trace']:
                self.assertIn('Emptystring', x, msg='Empty error')
            open('error.log', 'w')
        logmodule.logger.debug('Done')

class TestConfiguration(unittest.TestCase):
    def generate_config(self):
        path = os.path.join(os.getcwd(), 'tests')
        if not os.path.exists(path):
            os.mkdir(path)
        x = open(os.path.join(path, 'tests.conf'), 'w+')
        for i in ['[Mail server]', '{{example.com}}', 'ip = 127.0.0.1',
                  '[Mail]', '{{example@mail.com}}',
                  '[Checks]', '{{http://example.com}}', 'flag = url']:
            x.writelines(i + '\n')
        x.close()
        return path

    def test_get_section(self):
        logmodule.logger.debug('Start unittest configuration.py func - get_section')
        x = self.generate_config()
        y = (configuration.get_section(section='[Mail server]', path=x))
        self.assertTrue(y)
        self.assertEqual(len(y), 2)
        logmodule.logger.debug('Done')

    def test_get_val(self):
        logmodule.logger.debug('Start unittest configuration.py func - get_val')
        x = self.generate_config()
        y = configuration.get_val('[Mail]', path=x)
        self.assertTrue(y)
        self.assertEqual(len(y), 1)
        logmodule.logger.debug('Done')

if __name__ == '__main__':
    unittest.main()