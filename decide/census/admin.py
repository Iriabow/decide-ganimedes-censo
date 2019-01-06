from django.contrib import admin

from .models import Census


class CensusAdmin(admin.ModelAdmin):
    list_display = ('voting_id', 'voter_id')
    list_filter = ('voting_id', )

    search_fields = ('voter_id', )

    delete_confirmation_template = "delete_census.html"
    object_history_template = "census_history.html"
    change_list_template = "admin_index.html"

admin.site.register(Census, CensusAdmin)
