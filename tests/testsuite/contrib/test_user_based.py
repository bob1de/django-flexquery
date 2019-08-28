from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase
from django_flexquery import *
from django_flexquery.contrib.user_based import *
from django_flexquery_tests.models import *


class UserIsAnonymous(Exception):
    pass


class UserIsNone(Exception):
    pass


class UserBasedFlexQueryTestCase(TestCase):
    def setUp(self):
        class Man(Manager):
            @UserBasedFlexQuery.from_func
            def fq(base, user):
                if user is None:
                    raise UserIsNone
                if isinstance(user, AnonymousUser):
                    raise UserIsAnonymous
                return Q(a=42)

        self.man = Man()
        self.man.model = AModel
        self.req = RequestFactory().get("/")

        AModel.objects.create(a=24)
        AModel.objects.create(a=42)

    def test_user(self):
        self.assertEqual(self.man.fq(object).count(), 1)

    def test_request(self):
        self.req.user = object()
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

    def test_anonymous_user(self):
        self.req.user = AnonymousUser()
        with self.assertRaises(UserIsAnonymous):
            self.man.fq(self.req)
        self.man.fq.__class__.pass_anonymous_user = False
        self.assertEqual(self.man.fq(self.req).count(), 0)
