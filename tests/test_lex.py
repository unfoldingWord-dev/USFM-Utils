from __future__ import unicode_literals

import unittest

from usfm_utils.usfm.lex import UpdateablePosition

class UpdateablePositionTests(unittest.TestCase):
    def test_update(self):
        updateable_position = UpdateablePosition(index_from=1)
        updateable_position.update("hello")
        self.assertEqual(updateable_position.position.line, 1)
        self.assertEqual(updateable_position.position.col, 6)
        updateable_position.update("world\nhi")
        self.assertEqual(updateable_position.position.line, 2)
        self.assertEqual(updateable_position.position.col, 3)
        updateable_position.update("mars\n")
        self.assertEqual(updateable_position.position.line, 3)
        self.assertEqual(updateable_position.position.col, 1)
        updateable_position.update("line 3\n\u1234\u1235\n\nline\u23456")
        self.assertEqual(updateable_position.position.line, 6)
        self.assertEqual(updateable_position.position.col, 7)
