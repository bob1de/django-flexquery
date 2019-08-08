from django.db import models

from django_flexquery import *


q_func = lambda self: Q(a=42)

fq = FlexQuery.from_q(q_func)


class QS(QuerySet):
    fq = fq


class AModel(models.Model):
    objects = QS.as_manager()
    a = models.IntegerField()
