from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase
from django_flexquery import *
from django_flexquery.contrib.for_user import *
from django_flexquery_tests.models import *


class ForUserFlexQueryTestCase(TestCase):
    def setUp(self):
        class Man(Manager):
            @ForUserFlexQuery.from_func
            def fq(base, user):
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
        self.assertEqual(self.man.fq(self.req).count(), 2)

    def test_no_user_all(self):
        self.assertEqual(self.man.fq(None).count(), 2)

    def test_no_user_none(self):
        self.man.fq.__class__.none_if_no_user = True
        self.assertEqual(self.man.fq(None).count(), 0)
