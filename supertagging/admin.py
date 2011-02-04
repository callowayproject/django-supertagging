from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

from supertagging.models import SuperTag, SuperTaggedItem, SuperTagRelation
from supertagging.models import SuperTaggedRelationItem, SuperTagProcessQueue

from supertagging.settings import INCLUDE_DISPLAY_FIELDS

def lock_items(modeladmin, request, queryset):
    queryset.update(locked=True)
lock_items.short_description = "Lock selected Queue Items"

def unlock_items(modeladmin, request, queryset):
    queryset.update(locked=False)
unlock_items.short_description = "Unlock selected Queue Items"

class SuperTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'substitute', 'stype')
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
    list_display = ('content_object', 'tag', 'field', 'process_type', 'relevance', 'item_date')
    list_filter = ('process_type', 'field')
    search_fields = ('tag__name',)
    
    raw_id_fields = ('tag',)
    
    
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
