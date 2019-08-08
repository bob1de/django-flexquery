from django.test import SimpleTestCase
from django_flexquery import Q


class QTestCase(SimpleTestCase):
    def setUp(self):
        self.q = (~Q(a=42) | Q(b=43) & Q(c=44)).prefix("x")

    def test_prefix_copies_connector(self):
        self.assertEqual(self.q.connector, Q.OR)

    def test_prefix_copies_negated(self):
        self.assertTrue(self.q.children[0].negated, True)

    def test_prefix_keys(self):
        self.assertEqual(self.q.children[0].children[0][0], "x__a")
        self.assertEqual(self.q.children[1].children[0][0], "x__b")
        self.assertEqual(self.q.children[1].children[1][0], "x__c")
