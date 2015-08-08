# -*- encoding: utf-8 -*-
import os

from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.files.storage import FileSystemStorage
from django.core.paginator import (
    EmptyPage,
    PageNotAnInteger,
    Paginator,
)
from django.db import transaction
from django.db.models import get_model
from django.http import HttpResponseRedirect
from django.views.generic import (
    CreateView,
    DeleteView,
    UpdateView,
    TemplateView,
)

from braces.views import (
    LoginRequiredMixin,
    StaffuserRequiredMixin,
)
from formtools.wizard.views import SessionWizardView

from base.view_utils import BaseMixin
from .forms import (
    DocumentForm,
    DocumentListForm,
    LinkTypeForm,
    URLExternalLinkForm,
    PageListForm,
)
from .models import (
    BlockError,
    Link,
    Page,
    PageSection,
    Section,
    ViewUrl,
)


def _get_block_model(page_section):
    block_model = apps.get_model(
        page_section.section.block_app,
        page_section.section.block_model,
    )
    if not block_model:
        raise BlockError("Block model '{}.{}' does not exist.".format(
            page_section.section.block_app,
            page_section.section.block_model,
        ))
    return block_model


def _paginate_section(qs, page_no, section):
    """Paginate the 'block_list' queryset, using page section properties."""
    if section.paginated:
        # this is the block that requires pagination
        if section.paginated.order_by_field:
            qs = qs.order_by(section.paginated.order_by_field)
        if section.paginated.items_per_page:
            paginator = Paginator(qs, section.paginated.items_per_page)
        try:
            qs = paginator.page(page_no)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            qs = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            qs = paginator.page(paginator.num_pages)
    return qs


class ContentPageMixin(BaseMixin):
    """Page information."""

    def get_context_data(self, **kwargs):
        context = super(ContentPageMixin, self).get_context_data(**kwargs)
        context.update(dict(
            page=self.get_page(),
            menu_list=Page.objects.menu(),
        ))
        return context

    def get_page(self):
        menu = self.kwargs.get('menu', None)
        page = self.kwargs.get('page', None)
        if not page:
            raise BlockError("no 'page' parameter in url")
        try:
            if menu:
                return Page.objects.get(slug=page, slug_menu=menu)
            else:
                return Page.objects.get(slug=page, slug_menu='')
        except Page.DoesNotExist:
            raise BlockError(
                "Page '{}', menu '{}' does not exist".format(page, menu)
            )

    def get_page_section(self):
        page = self.get_page()
        section = self.get_section()
        try:
            return PageSection.objects.get(page=page, section=section)
        except PageSection.DoesNotExist:
            raise BlockError(
                "Page section '{}/{}' does not exist".format(
                    page.slug,
                    section.slug,
                )
            )

    def get_section(self):
        section = self.kwargs.get('section', None)
        if not section:
            raise BlockError("no 'section' parameter in url")
        try:
            return Section.objects.get(slug=section)
        except Section.DoesNotExist:
            raise BlockError("Section '{}' does not exist".format(section))

    def get_success_url(self):
        return self.object.block.page_section.page.get_design_url()


class ContentCreateView(ContentPageMixin, BaseMixin, CreateView):

    def form_valid(self, form):
        self.object = form.save(commit=False)
        try:
            block = self.block_class(page_section=self.get_page_section())
        except AttributeError:
            raise BlockError(
                "You need to add the 'block_class' attribute "
                "to your '{}' class.".format(self.__class__.__name__)
            )
        block.save()
        self.object.block = block
        self.object.order = self.model.objects.next_order()
        return super(ContentCreateView, self).form_valid(form)


class ContentPublishView(BaseMixin, UpdateView):

    def form_valid(self, form):
        """Publish 'pending' content."""
        self.object = form.save(commit=False)
        self.object.block.publish(self.request.user)
        messages.info(
            self.request,
            "Published block, id {}".format(
                self.object.block.pk,
            )
        )
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return self.object.block.page_section.page.get_design_url()


class ContentRemoveView(BaseMixin, UpdateView):

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.block.remove(self.request.user)
        messages.info(
            self.request,
            "Removed block {}".format(
                self.object.block.pk,
            )
        )
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return self.object.block.page_section.page.get_design_url()


class ContentUpdateView(BaseMixin, UpdateView):

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.set_pending_edit()
        return super(ContentUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ContentUpdateView, self).get_context_data(**kwargs)
        context.update(dict(
            is_update=True,
        ))
        return context

    def get_section(self):
        return self.object.block.section

    def get_success_url(self):
        return self.object.block.page_section.page.get_design_url()


class ElementCreateView(BaseMixin, CreateView):
    """Update the parent (content) object so it knows it has been changed."""

    def form_valid(self, form):
        self.object = form.save(commit=False)
        content = self.object.get_parent()
        content.set_pending_edit()
        content.save()
        return super(ElementCreateView, self).form_valid(form)


class ElementDeleteView(BaseMixin, DeleteView):
    """Update the parent (content) object so it knows it has been changed."""

    def delete(self, request, *args, **kwargs):
        with transaction.atomic():
            result = super(ElementDeleteView, self).delete(
                request, *args, **kwargs
            )
            content = self.object.get_parent()
            content.set_pending_edit()
            content.save()
        return result


class ElementUpdateView(BaseMixin, UpdateView):
    """Update the parent (content) object so it knows it has been changed."""

    def form_valid(self, form):
        self.object = form.save(commit=False)
        content = self.object.get_parent()
        content.set_pending_edit()
        content.save()
        return super(ElementUpdateView, self).form_valid(form)


class PageTemplateMixin(object):

    def get_template_names(self) :
        page = self.get_page()
        if page.template_name:
            template_name = page.template_name
        else:
            raise BlockError(
                "Page '{}' has no 'template_name'".format(page.slug)
            )
        return [template_name,]


class PageDesignMixin(object):

    def get_context_data(self, **kwargs):
        context = super(PageDesignMixin, self).get_context_data(**kwargs)
        page = self.get_page()
        view_url = ViewUrl.objects.view_url(
            self.request.user, page, self.request.GET.get('view')
        )
        context.update(dict(
            design=True,
            is_block_page=True,
            view_url=view_url,
        ))
        for e in PageSection.objects.filter(page=page) :
            block_model = _get_block_model(e)
            qs = _paginate_section(
                block_model.objects.pending(e),
                self.request.GET.get('page'),
                e.section
            )
            context.update({
                '{}_list'.format(e.section.slug): qs,
            })
            create_url = e.section.create_url(page)
            if create_url:
                context.update({
                    '{}_create_url'.format(e.section.slug): create_url,
                })
        return context


class PageDesignView(
        LoginRequiredMixin, StaffuserRequiredMixin,
        PageDesignMixin, PageTemplateMixin, ContentPageMixin, TemplateView):
    pass


class PageMixin(object):

    def _check_url(self, page):
        """Check the page is being accessed using the correct URL."""
        if self.request.path == page.get_absolute_url():
            if page.is_custom:
                raise BlockError(
                    "This is a custom page, so the request path "
                    "should NOT match the absolute url: '{}'".format(
                        self.request.path
                    )
                )
        else:
            if page.is_custom:
                pass
            else:
                raise BlockError(
                    "'request.path' ('{}') does not match the absolute url: "
                    "('{}')".format(self.request.path, page.get_absolute_url())
                )

    def get_context_data(self, **kwargs):
        context = super(PageMixin, self).get_context_data(**kwargs)
        page = self.get_page()
        self._check_url(page)
        context.update(dict(
            design=False,
            is_block_page=True,
        ))
        for e in PageSection.objects.filter(page=page):
            block_model = _get_block_model(e)
            qs = _paginate_section(
                block_model.objects.published(e),
                self.request.GET.get('page'),
                e.section
            )
            context.update({
                '{}_list'.format(e.section.slug): qs,
            })
        return context


class PageFormMixin(PageMixin, PageTemplateMixin, ContentPageMixin):
    pass


class PageView(PageMixin, PageTemplateMixin, ContentPageMixin, TemplateView):
    pass


# -----------------------------------------------------------------------------
# LinkWizard


def select_link_form(wizard, link_type) :
    """Return true if user has selected 'link_type'."""
    data = wizard.get_cleaned_data_for_step(LinkTypeForm.FORM_LINK_TYPE)
    selected_link_type = data['link_type'] if data else None
    return selected_link_type == link_type


def url_existing(wizard):
    """Return true if user opts for existing document link"""
    return select_link_form(wizard, LinkTypeForm.FORM_EXISTING)


def url_external_link(wizard):
    """Return true if user opts for external link """
    return select_link_form(wizard, LinkTypeForm.FORM_EXTERNAL_URL)


def url_internal_page(wizard):
    """Return true if user opts for an internal page """
    return select_link_form(wizard, LinkTypeForm.FORM_PAGE)


def url_upload(wizard):
    """Return true if user opts for upload a document """
    return select_link_form(wizard, LinkTypeForm.FORM_DOCUMENT)


class LinkWizard(LoginRequiredMixin, StaffuserRequiredMixin, SessionWizardView):
    """Link Wizard.

    The link wizard will allow the user to:

    1) Enter or edit an external URL e.g. http://www.bbc.co.uk/news
    2) Select an internal URL for a page on this web site.
    3) Select a document, or create a new document.

    Documentation for the SessionWizardView in
    http://django-formtools.readthedocs.org/en/latest/

    """

    condition_dict = {
        LinkTypeForm.FORM_EXTERNAL_URL: url_external_link,
        LinkTypeForm.FORM_PAGE: url_internal_page,
        LinkTypeForm.FORM_DOCUMENT: url_upload,
        LinkTypeForm.FORM_EXISTING: url_existing,
    }

    temp_dir = 'temp'
    file_storage = FileSystemStorage(
        location=os.path.join(settings.MEDIA_ROOT, 'temp/wizard')
    )
    # this list of forms must stay in this order!
    form_list = [
        (LinkTypeForm.FORM_LINK_TYPE, LinkTypeForm),
        (LinkTypeForm.FORM_EXTERNAL_URL, URLExternalLinkForm),
        (LinkTypeForm.FORM_PAGE, PageListForm),
        (LinkTypeForm.FORM_DOCUMENT, DocumentForm),
        (LinkTypeForm.FORM_EXISTING, DocumentListForm),
    ]

    form_link_type_map = {
        LinkTypeForm.FORM_DOCUMENT: Link.DOCUMENT,
        LinkTypeForm.FORM_EXISTING: Link.DOCUMENT,
        LinkTypeForm.FORM_EXTERNAL_URL: Link.URL_EXTERNAL,
        LinkTypeForm.FORM_PAGE: Link.URL_INTERNAL,
    }
    template_name = 'block/wizard.html'

    def _get_current_content_instance(self):
        content_pk = self.kwargs['content']
        pk = self.kwargs['pk']
        content_type = ContentType.objects.get(pk=content_pk)
        content_model = content_type.model_class()
        return content_model.objects.get(pk=pk)

    def _get_link_field_name(self, content_obj):
        """Assign the link to the field with this name."""
        return self.kwargs['field']

    def _save_link(self, form, content_obj, link_type):
         link = form.save(commit=False)
         link.link_type = link_type
         link = form.save()
         field_name = self._get_link_field_name(content_obj)
         setattr(content_obj, field_name, link)

    def done(self, form_list, form_dict, **kwargs):
        form_link_type = form_dict[LinkTypeForm.FORM_LINK_TYPE]
        form_id = form_link_type.cleaned_data['link_type']
        with transaction.atomic():
            obj = self._get_current_content_instance()
            if form_id == LinkTypeForm.REMOVE:
                obj.link = None
            else:
                form = form_dict[form_id]
                if form_id == LinkTypeForm.FORM_DOCUMENT:
                    form = form_dict[form_id]
                    document = form.save()
                    obj.link = Link.objects.create_document_link(document)
                else:
                    link_type = self.form_link_type_map[form_id]
                    self._save_link(form, obj, link_type)
            obj.set_pending_edit()
            obj.save()
        url = obj.block.page_section.page.get_design_url()
        return HttpResponseRedirect(url)
