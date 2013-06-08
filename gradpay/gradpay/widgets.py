# Django imports
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

from itertools import chain
from django.utils.html import escape, conditional_escape
from django.forms.widgets import SelectMultiple
from django.forms.widgets import flatatt

from selectable.forms import AutoCompleteWidget
class FKAutoCompleteWidget(AutoCompleteWidget):
  
    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            try:
                model_value = self.lookup_class.model.objects.get(pk=value)
            except:
                model_value = value
            final_attrs['value'] = force_unicode(self._format_value(model_value))
        return mark_safe(u'<input%s />' % flatatt(final_attrs))

class HelpSelectMultiple(SelectMultiple):
  
    def __init__(self, *args, **kwargs):
        self.help_texts = kwargs.pop('help_texts', [])
        self.help_place = kwargs.pop('help_place', '')
        super(HelpSelectMultiple, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<select multiple="multiple"%s>' % flatatt(final_attrs)]
        options = self.render_options(choices, value)
        if options:
            output.append(options)
        output.append('</select>')
        return mark_safe(u'\n'.join(output))

    def render_option(self, selected_choices, option_value, option_label, help_text=''):
        option_value = force_unicode(option_value)
        if option_value in selected_choices:
            selected_html = u' selected="selected"'
            if not self.allow_multiple_selected:
                # Only allow for a single selection.
                selected_choices.remove(option_value)
        else:
            selected_html = ''
        if help_text:
            help_html = u' parent-title="%s"' % (help_text)
            if self.help_place:
                help_html += u' parent-title-placement="%s"' % (self.help_place)
        else:
            help_html = ''
        return u'<option value="%s"%s%s>%s</option>' % (
            escape(option_value), selected_html, help_html,
            conditional_escape(force_unicode(option_label)))

    def render_options(self, choices, selected_choices):
        # Normalize to strings.
        selected_choices = set(force_unicode(v) for v in selected_choices)
        help_texts = self.help_texts[:]
        output = []
        for option_value, option_label in chain(self.choices, choices):
            if isinstance(option_label, (list, tuple)):
                output.append(u'<optgroup label="%s">' % escape(force_unicode(option_value)))
                for option in option_label:
                    output.append(self.render_option(selected_choices, *option))
                output.append(u'</optgroup>')
            else:
                try:
                    help_text = help_texts.pop(0)
                except:
                    help_text = ''
                output.append(self.render_option(selected_choices, option_value, option_label, help_text))
        return u'\n'.join(output)
