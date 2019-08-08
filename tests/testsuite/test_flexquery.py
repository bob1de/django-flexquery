from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django_flexquery import *
from django_flexquery.flexquery import InitializedFlexQueryType
from django_flexquery_tests.models import *


class FlexQueryTestCase(TestCase):
    def setUp(self):
        AModel.objects.create(a=24)
        AModel.objects.create(a=42)

    # Derive Manager from QuerySet

    def test_manager_from_queryset(self):
        class Man(Manager.from_queryset(QS)):
            pass

        self.assertTrue(hasattr(Man, "fq"))

    def test_queryset_as_manager(self):
        self.assertTrue(hasattr(AModel.objects, "fq"))

    # Sub-type creation

    def test_subtyping(self):
        self.assertTrue(isinstance(fq, InitializedFlexQueryType))
        self.assertTrue(issubclass(fq, FlexQuery))
        self.assertIs(fq.func, q_func)

    def test_invalid_func(self):
        with self.assertRaises(TypeError):
            FlexQuery.from_func("foo")

    # Invalid initialization

    def test_invalid_base(self):
        with self.assertRaises(TypeError):
            fq(object)

    # Access FlexQuery type as attribute

    def test_class_access(self):
        self.assertIs(QS.fq, fq)

    def test_object_access(self):
        self.assertTrue(isinstance(AModel.objects.fq, fq))

    # __repr__()

    def test_supertype_repr(self):
        self.assertEqual(repr(FlexQuery), type.__repr__(FlexQuery))

    def test_subtype_repr(self):
        self.assertEqual(repr(fq), r"<type FlexQuery %r>" % q_func.__name__)

    def test_object_repr(self):
        self.assertEqual(
            repr(AModel.objects.fq),
            r"<FlexQuery %r, bound to %r>" % (q_func.__name__, AModel.objects),
        )

    # FlexQuery.__call__()

    def test_call(self):
        self.assertTrue(AModel.objects.fq().count(), 1)

    # FlexQuery.as_q()

    def test_as_q(self):
        self.assertEqual(AModel.objects.fq.as_q(), Q(a=42))
