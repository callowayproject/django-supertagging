from django.contrib import admin

class SuperTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'stype', 'properties' )
    ordering = ('name', )
    search_fields = ('stype', 'name', )
    list_filter = ('stype', )
    
    
class SuperTaggedItemAdmin(admin.ModelAdmin):
    list_display = ('content_object', 'tag', 'field', 'relevance', 'instances')
    
    
class SuperTaggedRelationItemAdmin(admin.ModelAdmin):
    list_display = ('content_object', 'relation', 'field', 'instances')  
    
    
class SuperTagRelationAdmin(admin.ModelAdmin):
    list_display = ('tag', 'name', 'stype', 'properties')
    ordering = ('tag', )
    search_fields = ('stype', 'name', 'tag')
    list_filter = ('stype', 'name', )
