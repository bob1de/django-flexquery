from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase
from django_flexquery import *
from django_flexquery.contrib.user_based import *
from django_flexquery_tests.models import *


class UserIsNone(Exception):
    pass


class UserBasedFlexQueryTestCase(TestCase):
    def setUp(self):
        class Man(Manager):
            @UserBasedFlexQuery.from_func
            def fq(base, user):
                if user is None:
                    raise UserIsNone
                assert isinstance(user, AnonymousUser)
                return Q(a=42)

        self.man = Man()
        self.man.model = AModel
        self.req = RequestFactory().get("/")

        AModel.objects.create(a=24)
        AModel.objects.create(a=42)

    def test_user(self):
        self.assertEqual(self.man.fq(AnonymousUser()).count(), 1)

    def test_request(self):
        self.req.user = AnonymousUser()
        self.assertEqual(self.man.fq(self.req).count(), 1)

    def test_request_no_user(self):
        self.assertEqual(self.man.fq(self.req).count(), 0)

    def test_nub_all(self):
        self.man.fq.__class__.no_user_behavior = UserBasedFlexQuery.NUB_ALL
        self.assertEqual(self.man.fq(None).count(), 2)

    def test_nub_none(self):
        self.assertEqual(self.man.fq(None).count(), 0)

    def test_nub_pass(self):
        self.man.fq.__class__.no_user_behavior = UserBasedFlexQuery.NUB_PASS
        with self.assertRaises(UserIsNone):
            self.man.fq(None)
