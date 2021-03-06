# -*- encoding: utf-8 -*-
from base.form_utils import RequiredFieldForm

from .models import Title


class TitleForm(RequiredFieldForm):

    def __init__(self, *args, **kwargs):
        super(TitleForm, self).__init__(*args, **kwargs)
        for name in ('title',):
            self.fields[name].widget.attrs.update(
                {'class': 'pure-input-2-3'}
            )

    class Meta:
        model = Title
        fields = (
            'title',
            'picture',
        )
