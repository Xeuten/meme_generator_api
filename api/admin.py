from django.contrib import admin

from api.models import Meme, MemeTemplate


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


@admin.register(Meme)
class MemeAdmin(admin.ModelAdmin):
    list_display = ("template", "top_text", "bottom_text", "created_by")
    search_fields = ("template", "top_text", "bottom_text", "created_by")
    list_filter = ("template", "top_text", "bottom_text", "created_by")
    ordering = ("template", "top_text", "bottom_text", "created_by")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "template",
                    "top_text",
                    "bottom_text",
                    "created_by",
                )
            },
        ),
    )
