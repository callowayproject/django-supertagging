import django
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext, ugettext_lazy
from django.utils.encoding import force_unicode, smart_str
from django.http import HttpResponseRedirect

from supertagging.models import SuperTag, SuperTaggedItem, SuperTagRelation
from supertagging.models import SuperTaggedRelationItem, SuperTagProcessQueue

from supertagging.settings import INCLUDE_DISPLAY_FIELDS
from django.contrib.admin.views.main import (ChangeList, ALL_VAR, ORDER_VAR, 
                ORDER_TYPE_VAR, PAGE_VAR, SEARCH_VAR, TO_FIELD_VAR, 
                IS_POPUP_VAR, ERROR_FLAG)

class SupertagChangeList(ChangeList):
    """
    Lets list_editable work even if it is a popup
    """
    def __init__(self, request, model, list_display, list_display_links, list_filter, date_hierarchy, search_fields, list_select_related, list_per_page, list_editable, model_admin):
        self.model = model
        self.opts = model._meta
        self.lookup_opts = self.opts
        self.root_query_set = model_admin.queryset(request)
        self.list_display = list_display
        self.list_display_links = list_display_links
        self.list_filter = list_filter
        self.date_hierarchy = date_hierarchy
        self.search_fields = search_fields
        self.list_select_related = list_select_related
        self.list_per_page = list_per_page
        self.model_admin = model_admin
        
        # Get search parameters from the query string.
        try:
            self.page_num = int(request.GET.get(PAGE_VAR, 0))
        except ValueError:
            self.page_num = 0
        self.show_all = ALL_VAR in request.GET
        self.is_popup = IS_POPUP_VAR in request.GET
        self.to_field = request.GET.get(TO_FIELD_VAR)
        self.params = dict(request.GET.items())
        if PAGE_VAR in self.params:
            del self.params[PAGE_VAR]
        if ERROR_FLAG in self.params:
            del self.params[ERROR_FLAG]
        
        self.list_editable = list_editable
        self.order_field, self.order_type = self.get_ordering()
        self.query = request.GET.get(SEARCH_VAR, '')
        self.query_set = self.get_query_set()
        self.get_results(request)
        self.title = (self.is_popup and ugettext('Select %s') % force_unicode(self.opts.verbose_name) or ugettext('Select %s to change') % force_unicode(self.opts.verbose_name))
        self.filter_specs, self.has_filters = self.get_filters(request)
        self.pk_attname = self.lookup_opts.pk.attname

def lock_items(modeladmin, request, queryset):
    queryset.update(locked=True)
lock_items.short_description = "Lock selected Queue Items"

def unlock_items(modeladmin, request, queryset):
    queryset.update(locked=False)
unlock_items.short_description = "Unlock selected Queue Items"

class SuperTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'enabled', 'substitute', 'stype')
    ordering = ('name', )
    search_fields = ('stype', 'name', )
    list_filter = ('stype', )
    
    actions = ['disable_tag', 'enable_tag']
    
    raw_id_fields = ['substitute',]
    if INCLUDE_DISPLAY_FIELDS:
        raw_id_fields.append('related')
    
    def disable_tag(self, request, queryset):
        message_bit = ""
        for tag in queryset:
            message_bit = "%s %s," % (message_bit, tag.name)
            tag.enabled=False
            tag.save()
    
        self.message_user(request, "Tag(s): %s were Disabled." % message_bit)
    disable_tag.short_description = "Disable selected tags"
    
    
    def enable_tag(self, request, queryset):
        message_bit = ""
        for tag in queryset:
            message_bit = "%s %s," % (message_bit, tag.name)
            tag.enabled=True
            tag.save()
    
        self.message_user(request, "Tag(s): %s were Enabled." % message_bit)
    enable_tag.short_description = "Enable selected tags"
    
class SuperTaggedItemAdmin(admin.ModelAdmin):
    list_display = ('tag_name', 'tag_type', 'field', 'relevance_bar', 'ignore')
    # if django.VERSION[1] > 1:
    #     list_filter = ('field', 'tag__stype')
    # else:
    #     list_filter = ('field', )
    
    #search_fields = ('tag__name',)
    raw_id_fields = ('tag',)
    list_editable = ('ignore',)
    
    class Media:
        css = {'all': ('css/supertagloading.css',)}
        js = ('js/jquery.loading.1.6.4.min.js',)
    
    def tag_name(self, obj):
        if INCLUDE_DISPLAY_FIELDS:
            return obj.tag.display_name
        return obj.tag.name
    
    def tag_type(self, obj):
        return obj.tag.stype
    
    def get_changelist(self, request, **kwargs):
        """
        Returns the ChangeList class for use on the changelist page.
        """
        return SupertagChangeList
    
    def changelist_view(self, request, extra_context=None):
        if request.method == 'POST' and '_update_tags' in request.POST:
            ctype_id = request.GET.get(u'content_type__id', [False,])
            obj_id = request.GET.get('object_id', [False])
            if ctype_id == False or obj_id == False:
                return HttpResponseRedirect(request.get_full_path())
            ctype = ContentType.objects.get(id=ctype_id)
            obj = ctype.get_object_for_this_type(id=obj_id)
            from supertagging.modules import process
            process(obj)
            msg = "Supertags have been updated."
            self.message_user(request, msg)
            return HttpResponseRedirect(request.get_full_path())
        else:
            return super(SuperTaggedItemAdmin, self).changelist_view(request, extra_context)
    
    def relevance_bar(self, obj):
        from django.template import Context
        from django.template.loader import get_template
        if obj.relevance is not None:
            relevance = "%d%%" % (obj.relevance / 10.0)
        else:
            relevance = "0"
        
        tmpl = get_template("admin/supertagging/relevancebar.html")
        ctxt = Context({'relevance': relevance})
        return tmpl.render(ctxt)
    relevance_bar.allow_tags = True
    relevance_bar.admin_order_field = 'relevance'
    relevance_bar.short_description = 'Relevance'
    
    def get_actions(self, request):
        return []


class SuperTaggedRelationItemAdmin(admin.ModelAdmin):
    list_display = ('content_object', 'relation', 'field', 'process_type', 'item_date')  
    list_filter = ('process_type', 'field')
    
    raw_id_fields = ('relation',)
    
    
class SuperTagRelationAdmin(admin.ModelAdmin):
    list_display = ('tag', 'name', 'stype',)
    ordering = ('tag', )
    search_fields = ('stype', 'name', 'tag__name')
    list_filter = ('stype', 'name', )
    
    raw_id_fields = ('tag',)
    
    
class SuperTagProcessQueueAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'locked')
    actions = [lock_items, unlock_items]
    

admin.site.register(SuperTag, SuperTagAdmin)
admin.site.register(SuperTaggedItem, SuperTaggedItemAdmin)
admin.site.register(SuperTagRelation, SuperTagRelationAdmin)
admin.site.register(SuperTaggedRelationItem, SuperTaggedRelationItemAdmin)
admin.site.register(SuperTagProcessQueue, SuperTagProcessQueueAdmin)