from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import six
import os
import logging
import warnings

import pims
import trackpy
import trackpy.diag
from trackpy.tests.common import StrictTestCase
from trackpy.try_numba import NUMBA_AVAILABLE

import nose

path, _ = os.path.split(os.path.abspath(__file__))

class DiagTests(StrictTestCase):
    def test_performance_report(self):
        trackpy.diag.performance_report()

    def test_dependencies(self):
        trackpy.diag.dependencies()


class APITests(StrictTestCase):
    def test_pims_deprecation(self):
        """Using a pims class should work, but generate a warning.

        The inclusion of these classes (and therefore this test) in
        trackpy is deprecated as of v0.3 and will be removed in a future
        version."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter('ignore')
            warnings.simplefilter('always', UserWarning)
            imseq = trackpy.ImageSequence(os.path.join(path, 'video/image_sequence/*.png'))
            assert isinstance(imseq, pims.ImageSequence)
            if len(w) != 1:
                print('Caught warnings:')
                for wrn in w:
                    print(wrn, wrn.message)
            assert len(w) == 1


class LoggerTests(StrictTestCase):
    def test_heirarchy(self):
        self.assertTrue(trackpy.linking.logger.parent is trackpy.logger)
        self.assertTrue(trackpy.feature.logger.parent is trackpy.logger)
        self.assertTrue(trackpy.preprocessing.logger.parent is trackpy.logger)

    def test_convenience_funcs(self):
        trackpy.quiet(True)
        self.assertEqual(trackpy.logger.level, logging.WARN)
        trackpy.quiet(False)
        self.assertEqual(trackpy.logger.level, logging.INFO)

        trackpy.ignore_logging()
        self.assertEqual(len(trackpy.logger.handlers), 0)
        self.assertEqual(trackpy.logger.level, logging.NOTSET)
        self.assertTrue(trackpy.logger.propagate)

        trackpy.handle_logging()
        self.assertEqual(len(trackpy.logger.handlers), 1)
        self.assertEqual(trackpy.logger.level, logging.INFO)
        self.assertEqual(trackpy.logger.propagate, 1)


class NumbaTests(StrictTestCase):
    def setUp(self):
        if not NUMBA_AVAILABLE:
            raise nose.SkipTest("Numba not installed. Skipping.")
        self.funcs = trackpy.try_numba._registered_functions

    def test_registered_numba_functions(self):
        self.assertGreater(len(self.funcs), 0)

    def test_enabled(self):
        trackpy.enable_numba()
        for registered_func in self.funcs:
            module = __import__(registered_func.module_name, fromlist='.')
            func = getattr(module, registered_func.func_name)
            self.assertIs(func, registered_func.compiled)

    def test_disabled(self):
        trackpy.disable_numba()
        for registered_func in self.funcs:
            module = __import__(registered_func.module_name, fromlist='.')
            func = getattr(module, registered_func.func_name)
            self.assertIs(func, registered_func.ordinary)