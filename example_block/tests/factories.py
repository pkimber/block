# -*- encoding: utf-8 -*-
import factory

from block.tests.factories import PageSectionFactory
from example_block.models import (
    Title,
    TitleBlock,
    TitleImage,
    TitleLink,
)


class TitleBlockFactory(factory.django.DjangoModelFactory):

    page_section = factory.SubFactory(PageSectionFactory)

    class Meta:
        model = TitleBlock


class TitleFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Title

    block = factory.SubFactory(TitleBlockFactory)

    @factory.sequence
    def order(n):
        return n


class TitleImageFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = TitleImage


class TitleLinkFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = TitleLink
