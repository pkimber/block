# -*- encoding: utf-8 -*-
from django.conf.urls import url

from block.views import (
    WizardImageChoose,
    WizardImageOption,
    WizardImageOrder,
    WizardImageRemove,
    WizardImageSelect,
    WizardImageUpload,
    WizardLinkChoose,
    WizardLinkExternal,
    WizardLinkOption,
    WizardLinkOrder,
    WizardLinkPage,
    WizardLinkRemove,
    WizardLinkSelect,
    WizardLinkUpload,
)


urlpatterns = [
    # image wizard
    url(regex=r'^image/(?P<content>\d+)/(?P<pk>\d+)/(?P<field>[-\w\d]+)/'
        r'(?P<type>[-\w\d]+)/choose/$',
        view=WizardImageChoose.as_view(),
        name='block.wizard.image.choose'
        ),
    url(regex=r'^image/(?P<content>\d+)/(?P<pk>\d+)/(?P<field>[-\w\d]+)/'
        r'(?P<type>[-\w\d]+)/(?P<category>[-\w\d]+)/choose/$',
        view=WizardImageChoose.as_view(),
        name='block.wizard.image.choose'
        ),
    url(regex=r'^image/(?P<content>\d+)/(?P<pk>\d+)/(?P<field>[-\w\d]+)/'
        r'(?P<type>[-\w\d]+)/order/$',
        view=WizardImageOrder.as_view(),
        name='block.wizard.image.order'
        ),
    url(regex=r'^image/(?P<content>\d+)/(?P<pk>\d+)/(?P<field>[-\w\d]+)/'
        r'(?P<type>[-\w\d]+)/option/$',
        view=WizardImageOption.as_view(),
        name='block.wizard.image.option'
        ),
    url(regex=r'^image/(?P<content>\d+)/(?P<pk>\d+)/(?P<field>[-\w\d]+)/'
        r'(?P<type>[-\w\d]+)/remove/$',
        view=WizardImageRemove.as_view(),
        name='block.wizard.image.remove'
        ),
    url(regex=r'^image/(?P<content>\d+)/(?P<pk>\d+)/(?P<field>[-\w\d]+)/'
        r'(?P<type>[-\w\d]+)/select/$',
        view=WizardImageSelect.as_view(),
        name='block.wizard.image.select'
        ),
    url(regex=r'^image/(?P<content>\d+)/(?P<pk>\d+)/(?P<field>[-\w\d]+)/'
        r'(?P<type>[-\w\d]+)/upload/$',
        view=WizardImageUpload.as_view(),
        name='block.wizard.image.upload'
        ),
    # link wizard
    url(regex=r'^link/(?P<content>\d+)/(?P<pk>\d+)/(?P<field>[-\w\d]+)/'
        r'(?P<type>[-\w\d]+)/choose/$',
        view=WizardLinkChoose.as_view(),
        name='block.wizard.link.choose'
        ),
    url(regex=r'^link/(?P<content>\d+)/(?P<pk>\d+)/(?P<field>[-\w\d]+)/'
        '(?P<type>[-\w\d]+)/(?P<category>[-\w\d]+)/choose/$',
        view=WizardLinkChoose.as_view(),
        name='block.wizard.link.choose'
        ),
    url(regex=r'^link/(?P<content>\d+)/(?P<pk>\d+)/(?P<field>[-\w\d]+)/'
        '(?P<type>[-\w\d]+)/external/$',
        view=WizardLinkExternal.as_view(),
        name='block.wizard.link.external'
        ),
    url(regex=r'^link/(?P<content>\d+)/(?P<pk>\d+)/(?P<field>[-\w\d]+)/'
        r'(?P<type>[-\w\d]+)/option/$',
        view=WizardLinkOption.as_view(),
        name='block.wizard.link.option'
        ),
    url(regex=r'^link/(?P<content>\d+)/(?P<pk>\d+)/(?P<field>[-\w\d]+)/'
        r'(?P<type>[-\w\d]+)/order/$',
        view=WizardLinkOrder.as_view(),
        name='block.wizard.link.order'
        ),
    url(regex=r'^link/(?P<content>\d+)/(?P<pk>\d+)/(?P<field>[-\w\d]+)/'
        r'(?P<type>[-\w\d]+)/remove/$',
        view=WizardLinkRemove.as_view(),
        name='block.wizard.link.remove'
        ),
    url(regex=r'^link/(?P<content>\d+)/(?P<pk>\d+)/(?P<field>[-\w\d]+)/'
        r'(?P<type>[-\w\d]+)/select/$',
        view=WizardLinkSelect.as_view(),
        name='block.wizard.link.select'
        ),
    url(regex=r'^link/(?P<content>\d+)/(?P<pk>\d+)/(?P<field>[-\w\d]+)/'
        r'(?P<type>[-\w\d]+)/upload/$',
        view=WizardLinkUpload.as_view(),
        name='block.wizard.link.upload'
        ),
    url(regex=r'^link/(?P<content>\d+)/(?P<pk>\d+)/(?P<field>[-\w\d]+)/'
        r'(?P<type>[-\w\d]+)/page/$',
        view=WizardLinkPage.as_view(),
        name='block.wizard.link.page'
        ),
]
