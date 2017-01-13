# -*- coding:utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import with_statement

import os
import sys
import unittest

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    testSuite = unittest.TestSuite()
    suite = unittest.TestLoader().discover('tests', pattern='*_test.py')
    testSuite.addTest(suite)

    return testSuite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(main())
