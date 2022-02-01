from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.encoding import force_str as force_text


def time_format(field, date_format=None, description=None):
    """
    Format a `DateField` or `DateTimeField` as string in a given format `date_format`.
    WARNING: Dont use plain user-input for the field name, as the field name is being used in a eval statement!
    """
    def time(self, obj=None):
        if not obj:
            return ''
        return timezone.localtime(eval('obj.%s' % field)).strftime(date_format) # pylint: disable=W0123
    time.short_description = description
    return time

def foreign_key_link(field, description=None, link=None):
    """
    Get a link to the change view of a related object. It's possible to use fields of a related model.
    WARNING: Dont use plain user-input for the field name, as the field name is being used in a eval statement!
    """
    def change_link(self, obj=None):
        if obj.pk:
            url = reverse('admin:%s_%s_change' % (eval('obj.%s._meta.app_label' % field), eval('obj.%s._meta.model_name' % field)), args=[force_text(eval('obj.%s.pk' % field))]) # pylint: disable=W0123
            return format_html('<a href="{}">{}</a>', url, link or str(eval('obj.%s' % field))) # pylint: disable=W0123
        return ""
    change_link.short_description = description
    return change_link

def one_to_many_link(field, related_field, description=None, link=None):
    """
    Get a link to a list view containing the related objects. It's possible to use fields of a related model.
    WARNING: Dont use plain user-input for the field name, as the field name is being used in a eval statement!
    """
    def changelist_link(self, obj=None):
        if not obj:
            return ''
        url = reverse('admin:%s_%s_changelist' % (eval('obj.%s.model._meta.app_label' % field), eval('obj.%s.model._meta.model_name' % field))) # pylint: disable=W0123
        return format_html('<a href="{}?{}={}">{}</a>', url, related_field, obj.pk, link or "Show " + str(eval('obj.%s.model._meta.model_name' % field))) # pylint: disable=W0123
    changelist_link.short_description = description
    return changelist_link

def get_edit_link(description='Edit'):
    """
    Get a link with a changelink icon inside to the change view of a related object.
    """
    def edit_link(self, obj=None):
        if obj.pk:
            url = reverse('admin:%s_%s_change' % (obj._meta.app_label, obj._meta.model_name), args=[force_text(obj.pk)])
            return format_html('<a href="{}"><img src="/static/admin/img/icon-changelink.svg"></a>', url)
        return ""
    edit_link.short_description = description
    return edit_link
