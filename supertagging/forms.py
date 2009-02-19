"""
Tagging components for Django's form library.
"""
from django import forms
from django.utils.translation import ugettext as _

from supertagging import settings
from supertagging.models import SuperTag
from supertagging.utils import parse_tag_input

class AdminSuperTagForm(forms.ModelForm):
    class Meta:
        model = SuperTag

    def clean_name(self):
        value = self.cleaned_data['name']
        tag_names = parse_tag_input(value)
        if len(tag_names) > 1:
            raise ValidationError(_('Multiple tags were given.'))
        #elif len(tag_names[0]) > settings.MAX_TAG_LENGTH:
        #    raise forms.ValidationError(
        #        _('A tag may be no more than %s characters long.') %
        #            settings.MAX_TAG_LENGTH)
        return value

class SuperTagField(forms.CharField):
    """
    A ``CharField`` which validates that its input is a valid list of
    tag names.
    """
    def clean(self, value):
        value = super(SuperTagField, self).clean(value)
        if value == u'':
            return value
        #for tag_name in parse_tag_input(value):
        #    if len(tag_name) > settings.MAX_TAG_LENGTH:
        #        raise forms.ValidationError(
        #            _('Each tag may be no more than %s characters long.') %
        #                settings.MAX_TAG_LENGTH)
        return value