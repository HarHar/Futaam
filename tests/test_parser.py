# -*- coding: utf-8 -*-
"""
This file is part of Futaam.

Futaam is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Futaam is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Futaam. If not, see <http://www.gnu.org/licenses/>.
"""
import unittest
import os
from interfaces.common import parser


class TestDbCreation(unittest.TestCase):

    def setUp(self):
        self.items = [{"status": "w", "hash": "123imahash", "name":
                      "Neon Genesis Evangelion", "id": 0, "lastwatched": 26,
                      "genre": "genres here", "aid": 30, "type": "anime",
                      "obs": "Best Anime Ever"}]

    def test_json_creation(self):
        parser.createDB("test3.db", "json", "test json db creation")
        self.assertTrue(os.path.exists("test3.db"))
        os.unlink("test3.db")

    def test_json_creation_with_items(self):
        parser.createDB(
            "test4.db", "json", "test json db creation with items", self.items)
        self.assertTrue(os.path.exists("test4.db"))
        os.unlink("test4.db")
