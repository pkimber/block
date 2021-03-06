# -*- encoding: utf-8 -*-
from django.db import IntegrityError

from block.models import BlockError


def check_content(
            model_instance, ignore_remove=None, check_elements=None):
    """Call the standard methods used by the block content.

    An exception will be thrown if the method is not defined
    """
    # check the page methods
    model_instance.block.page_section.page.get_absolute_url()
    # check the standard URLs
    model_instance.url_publish()
    check_urledit(model_instance)

    if model_instance.has_elements():
        model_instance.url_elements()
    if ignore_remove:
        if hasattr(model_instance, 'url_remove'):
            raise BlockError(
                "The content model has the 'url_remove' method, but "
                "you have chosen not to test it (see 'ignore_remove' "
                "in 'check_content_methods')"
            )
    else:
        model_instance.url_remove()
    model_instance.url_update()
    # check the 'content' set
    try:
        model_instance.block.content.all()
    except AttributeError:
        raise BlockError(
            "The 'block' field in the content model does not have "
            "a 'related_name' (should be set to 'content')"
        )
    # check the string method
    str(model_instance)
    # check the unique together constraint
    try:
        model_instance.pk = 0
        model_instance.save()
        raise BlockError(
            "Missing 'unique_together' on {} ("
            "unique_together = ('block', 'moderate_state'))"
            "".format(model_instance.__class__)
        )
    except IntegrityError:
        pass
    # check the order field
    try:
        model_instance.order
    except AttributeError:
        raise BlockError(
            "The {} model does not have an 'order' field"
            "".format(model_instance.__class__)
        )
    # check the wizard fields
    #try:
    #    model_instance.wizard_fields
    #except AttributeError:
    #    raise BlockError(
    #        "The {} model does not have a 'wizard_fields' property"
    #        "".format(model_instance.__class__)
    #    )


def check_element(model_instance):
    """Call the standard methods used by an element.

    An exception will be thrown if the method is not defined
    """
    # check the element attributes
    model_instance.get_parent()

def check_urledit(model_instance):
    """Call the standard methods used by a model with a url

    An exception will be thrown if the method is not defined
    """
    # check the url attributes
    if ('has_url' in dir(model_instance)):
        model_instance.get_url_text()
        model_instance.get_url_link()
        model_instance.set_url('', '')
        model_instance.url_urledit()
