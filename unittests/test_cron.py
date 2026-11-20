import os
import tempfile
import unittest
from unittest.mock import patch

from unittests import base

import cron
import asm3.dbupdate


class TestCron(unittest.TestCase):

    def test_run_finds_database_updates_outside_install_directory(self):
        dbo = cron.db.get_dbo("SQLITE")
        dbo.installpath = base.get_dbo().installpath
        original_directory = os.getcwd()
        expected_updates = asm3.dbupdate._dbupdates_list(dbo)
        self.assertTrue(expected_updates)

        def read_updates(database):
            self.assertEqual(asm3.dbupdate._dbupdates_list(database), expected_updates)

        try:
            with tempfile.TemporaryDirectory() as directory:
                os.chdir(directory)
                with patch.object(cron, "maint_db_install", side_effect=read_updates) as task, \
                        patch.object(cron.al, "info"), patch.object(cron.al, "debug"):
                    cron.run(dbo, "maint_db_install")
                    task.assert_called_once_with(dbo)
                self.assertEqual(os.getcwd(), directory)
        finally:
            os.chdir(original_directory)
