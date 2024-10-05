from django.contrib import admin

from api.models import MemeTemplate


@admin.register(MemeTemplate)
class MemeTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "image_url", "default_top_text", "default_bottom_text")
    search_fields = ("name", "image_url", "default_top_text", "default_bottom_text")
    list_filter = ("name", "image_url", "default_top_text", "default_bottom_text")
    ordering = ("name", "image_url", "default_top_text", "default_bottom_text")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "image_url",
                    "default_top_text",
                    "default_bottom_text",
                )
            },
        ),
    )
