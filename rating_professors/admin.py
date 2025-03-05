from django.contrib import admin
from .models import Professor, Module, ModuleInstance, Rating

# admin.site.register(Professor)
# admin.site.register(Module)
# admin.site.register(ModuleInstance)
# admin.site.register(Rating)

@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'department')
    search_fields = ('name', 'email')
    list_filter = ('department',)

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'credits')
    search_fields = ('code', 'title')

@admin.register(ModuleInstance)
class ModuleInstanceAdmin(admin.ModelAdmin):
    list_display = ('module', 'year', 'semester')
    list_filter = ('year', 'semester')
    filter_horizontal = ('professors',)  # For easier many-to-many selection

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'professor', 'module_instance', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'professor__name', 'module_instance__module__code')