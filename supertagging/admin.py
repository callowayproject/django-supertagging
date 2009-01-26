from django.contrib import admin

class SuperTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'properties' )
    ordering = ('name', )
    search_fields = ('type', 'name', )
    list_filter = ('type', )
    
    
class SuperTaggedItemAdmin(admin.ModelAdmin):
    list_display = ('content_object', 'tag', 'field', 'relevance', 'instances')
    
    
class SuperTaggedRelationItemAdmin(admin.ModelAdmin):
    list_display = ('content_object', 'relation', 'field', 'instances')  
    
    
class SuperTagRelationAdmin(admin.ModelAdmin):
    list_display = ('tag', 'name', 'type', 'properties')
    ordering = ('tag', )
    search_fields = ('type', 'name', 'tag')
    list_filter = ('type', 'name', )
