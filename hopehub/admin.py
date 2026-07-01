# ======================================================================
# FILE: hopehub/admin.py (PATCH 1 OF 1)
# START: CLINICAL_GOVERNANCE_PRODUCTION_DASHBOARD
# ======================================================================
from django.contrib import admin
from hopehub.models import JournalEntry, Tag, Category, GovernanceSection, TechnicalConstraint

@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'emotion', 'mood_rating', 'created_at', 'updated_at')
    search_fields = ('text', 'emotion', 'user__username')
    list_filter = ('emotion', 'mood_rating', 'created_at')
    ordering = ('-created_at',)
    # Expose the read-only User UUID token automatically inside forms
    readonly_fields = ('display_user_uuid',)

    def display_user_uuid(self, obj):
        return obj.user.id if obj.user else "-"
    display_user_uuid.short_description = "Patient / Developer UUID Token"

@admin.register(GovernanceSection)
class GovernanceSectionAdmin(admin.ModelAdmin):
    list_display = ('regulation_type', 'title', 'updated_at')
    list_filter = ('regulation_type',)

@admin.register(TechnicalConstraint)
class TechnicalConstraintAdmin(admin.ModelAdmin):
    list_display = ('rule_key', 'description', 'is_active')
    list_filter = ('is_active',)

admin.site.register(Tag)
admin.site.register(Category)
# ======================================================================
# END: CLINICAL_GOVERNANCE_PRODUCTION_DASHBOARD (PATCH 1 OF 1)
# ======================================================================
