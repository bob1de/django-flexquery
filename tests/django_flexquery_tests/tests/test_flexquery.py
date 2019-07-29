import re

from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.test import TestCase

from django_flexquery import *


qs_func = lambda qs: qs.filter(a=42)
q_func = lambda: Q(a=42)

fq_from_qs = FlexQuery.from_queryset(qs_func)
fq_from_q = FlexQuery.from_q(q_func)


class QS(QuerySet):
    fq_from_qs = fq_from_qs
    fq_from_q = fq_from_q


class AModel(models.Model):
    objects = QS.as_manager()
    a = models.IntegerField()


class FlexQueryTestCase(TestCase):
    def setUp(self):
        AModel.objects.create(a=24)
        AModel.objects.create(a=42)

    # Derive Manager from QuerySet

    def test_manager_from_queryset(self):
        class Man(Manager.from_queryset(QS)):
            pass

        self.assertTrue(hasattr(Man, "fq_from_q"))

    def test_queryset_as_manager(self):
        self.assertTrue(hasattr(AModel.objects, "fq_from_q"))

    # Sub-type creation

    def test_from_queryset(self):
        self.assertTrue(isinstance(fq_from_qs, type(FlexQuery)))
        self.assertTrue(issubclass(fq_from_qs, FlexQuery))
        self.assertIs(fq_from_qs.qs_func, qs_func)
        self.assertIs(fq_from_qs.q_func, None)

    def test_from_q(self):
        self.assertTrue(isinstance(fq_from_q, type(FlexQuery)))
        self.assertTrue(issubclass(fq_from_q, FlexQuery))
        self.assertIs(fq_from_q.qs_func, None)
        self.assertIs(fq_from_q.q_func, q_func)

    # Repeated sub-typing

    def test_repeated_subtyping(self):
        with self.assertRaises(NotImplementedError):
            fq_from_qs.from_queryset(qs_func)
        with self.assertRaises(NotImplementedError):
            fq_from_q.from_q(q_func)

    # Invalid initialization

    def test_invalid_base(self):
        Some = type("Some", (), {"fq_from_q": fq_from_q})
        with self.assertRaises(TypeError):
            fq_from_q(object)

    def test_initialize_supertype(self):
        with self.assertRaises(ImproperlyConfigured):
            FlexQuery(AModel.objects)

    # Access FlexQuery type as attribute

    def test_class_access(self):
        self.assertIs(QS.fq_from_q, fq_from_q)

    def test_object_access(self):
        self.assertTrue(isinstance(AModel.objects.fq_from_q, fq_from_q))

    # __repr__()

    def test_supertype_repr(self):
        self.assertEqual(repr(FlexQuery), type.__repr__(FlexQuery))
        self.assertEqual(
            repr(fq_from_q), "<type FlexQueryFromQFunction %r>" % q_func.__name__
        )

    def test_subtype_repr(self):
        self.assertEqual(
            repr(fq_from_q),
            r"<type FlexQueryFromQFunction %r>" % fq_from_q.q_func.__name__,
        )

    def test_object_repr(self):
        bound = AModel.objects.fq_from_q
        self.assertEqual(
            repr(bound),
            r"<FlexQueryFromQFunction %r, bound to %r>"
            % (bound.q_func.__name__, bound.base),
        )

    # FlexQuery.__call__()

    def test_qs_native(self):
        self.assertTrue(AModel.objects.fq_from_qs().count(), 1)

    def test_q_to_qs(self):
        self.assertTrue(AModel.objects.fq_from_q().count(), 1)

    # FlexQuery.as_q()

    def test_qs_to_q(self):
        q = AModel.objects.fq_from_qs.as_q()
        self.assertEqual(len(q), 1)
        self.assertEqual(q.children[0][0], "pk__in")
        self.assertTrue(isinstance(q.children[0][1], QuerySet))

    def test_q_native(self):
        self.assertEqual(AModel.objects.fq_from_q.as_q(), Q(a=42))
