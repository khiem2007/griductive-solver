import unittest

from proofledger.reasoning.regions import resolve_region


class RegionTests(unittest.TestCase):
    def test_membership(self):
        self.assertEqual(("A2", "B2", "C2"), resolve_region({"kind": "ROW", "index": 2}, 3))
        self.assertEqual(("B1", "B2", "B3"), resolve_region({"kind": "COLUMN", "index": "b"}, 3))
        self.assertEqual({"B1", "A2", "B2"}, set(resolve_region({
            "kind": "NEIGHBORS", "cell": "a1"}, 3)))
        self.assertEqual(8, len(resolve_region({"kind": "NEIGHBORS", "cell": "B2"}, 3)))
        self.assertEqual({"A1", "C1", "A3", "C3"}, set(resolve_region({"kind": "CORNERS"}, 3)))
        self.assertEqual(12, len(resolve_region({"kind": "BOUNDARY"}, 4)))
        self.assertEqual(("C2", "A1"), resolve_region({"kind": "EXPLICIT", "cells": ["c2", "A1"]}, 3))

    def test_invalid_regions(self):
        for region in ({"kind": "ROW", "index": 0}, {"kind": "COLUMN", "index": "D"},
                       {"kind": "ROW", "index": True}, {"kind": "EXPLICIT", "cells": []},
                       {"kind": "EXPLICIT", "cells": ["A1", "a1"]},
                       {"kind": "EXPLICIT", "cells": ["A01"]},
                       {"kind": "NEIGHBORS", "cell": "Z3"}, {"kind": "UNKNOWN"}):
            with self.subTest(region=region), self.assertRaises(ValueError):
                resolve_region(region, 3)
