from django.contrib import admin
from .models import Professor, Module, ModuleInstance, Rating


@admin.register(Professor)
class ProfessorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'department')
    search_fields = ('name', 'email')
    list_filter = ('department',)

    def average_rating(self, obj):
        return obj.get_average_rating()
    average_rating.short_description = 'Average Rating'

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'credits')
    search_fields = ('code', 'title')

    def instance_count(self, obj):
        return obj.instances.count()
    instance_count.short_description = 'Instance Count'

@admin.register(ModuleInstance)
class ModuleInstanceAdmin(admin.ModelAdmin):
    list_display = ('module', 'year', 'semester')
    list_filter = ('year', 'semester')
    filter_horizontal = ('professors',)

    def professor_list(self, obj):
        return ", ".join([professor.name for professor in obj.professors.all()])
    professor_list.short_description = 'Professors' 

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'professor', 'module_instance', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'professor__name', 'module_instance__module__code')