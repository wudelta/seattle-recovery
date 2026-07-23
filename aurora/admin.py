# ======================================================================
# FILE: aurora/admin.py (PATCH 1 OF 5)
# START: COMPONENT_REGISTRY_ADMIN
# ======================================================================
from django.contrib import admin
from django.utils.safestring import mark_safe

from aurora.models import (
    ChatLedgerEntry,
    ComponentRegistry,
    DeltaDirectives,
    DeltaNotesEntry,
    Initiative,
    PendingCodeChange,
    Phase,
    StaticContent,
    Step,
)


@admin.register(ComponentRegistry)
class ComponentRegistryAdmin(admin.ModelAdmin):
    """Exposes the tracked system assets visually for manual documentation."""

    list_display = (
        'name',
        'file_path',
        'persona',
        'status',
        'visibility',
        'locked',
        'display_user_uuid',
        'date_modified',
    )
    search_fields = (
        'name',
        'file_path',
        'description',
        'created_by__username',
    )
    list_filter = (
        'persona',
        'status',
        'visibility',
        'locked',
    )
    readonly_fields = (
        'id',
        'display_developer_docs',
        'display_stakeholder_docs',
        'display_user_uuid',
        'date_created',
        'date_modified',
    )
    list_select_related = ('created_by',)

    fieldsets = (
        ('System Identity Parity Anchors', {
            'fields': (
                'id',
                'name',
                'file_path',
                'persona',
                'visibility',
            )
        }),
        ('Safety Locks & Deployment Status', {
            'fields': (
                'status',
                'locked',
                'created_by',
                'display_user_uuid',
            )
        }),
        ('Unified Summary String', {
            'fields': ('description',)
        }),
        ('🔍 Detailed Multi-Audience AI Documentation (Formatted View)', {
            'fields': (
                'display_developer_docs',
                'display_stakeholder_docs',
            ),
        }),
        ('Record History', {
            'fields': (
                'date_created',
                'date_modified',
            ),
        }),
    )

    def display_user_uuid(self, obj):
        """Displays the secure, un-incremented UUID token of the owner."""
        return obj.created_by_id or "-"

    display_user_uuid.short_description = "Owner UUID Token"

    def display_developer_docs(self, obj):
        """Extracts and safely formats the developer documentation track."""
        docs = obj.description_audiences or {}
        text = docs.get(
            "developer_docs",
            "No documentation generated yet.",
        )
        formatted_text = text.replace('\n', '<br>')

        return mark_safe(
            '<div style="background:#f8f9fa; padding:15px; '
            'border-left:4px solid #007bff; border-radius:4px; '
            'max-width:800px; font-family:sans-serif; line-height:1.5;">'
            f'{formatted_text}</div>'
        )

    display_developer_docs.short_description = (
        "Developer Architecture Overview"
    )

    def display_stakeholder_docs(self, obj):
        """Extracts and safely formats the stakeholder documentation track."""
        docs = obj.description_audiences or {}
        text = docs.get(
            "stakeholder_docs",
            "No documentation generated yet.",
        )
        formatted_text = text.replace('\n', '<br>')

        return mark_safe(
            '<div style="background:#f8f9fa; padding:15px; '
            'border-left:4px solid #28a745; border-radius:4px; '
            'max-width:800px; font-family:sans-serif; line-height:1.5;">'
            f'{formatted_text}</div>'
        )

    display_stakeholder_docs.short_description = (
        "Stakeholder Business Translation"
    )
# ======================================================================
# END: COMPONENT_REGISTRY_ADMIN (PATCH 1 OF 5)
# ======================================================================

# ======================================================================
# FILE: aurora/admin.py (PATCH 2 OF 5)
# START: CONTENT_AND_DIRECTIVES_ADMIN
# ======================================================================
@admin.register(StaticContent)
class StaticContentAdmin(admin.ModelAdmin):
    """Management grid for standalone informational content."""

    list_display = (
        'title',
        'application',
        'created_by',
        'display_user_uuid',
        'date_created',
        'date_modified',
    )
    search_fields = (
        'title',
        'html_content',
        'created_by__username',
    )
    list_filter = (
        'application',
        'date_created',
        'date_modified',
        'created_by',
    )
    readonly_fields = (
        'id',
        'display_user_uuid',
        'date_created',
        'date_modified',
    )
    ordering = ('-date_created',)
    list_select_related = ('created_by',)

    fieldsets = (
        ('Content Identity', {
            'fields': (
                'id',
                'application',
                'title',
            ),
        }),
        ('HTML Content', {
            'fields': ('html_content',),
        }),
        ('Ownership', {
            'fields': (
                'created_by',
                'display_user_uuid',
            ),
        }),
        ('Record History', {
            'fields': (
                'date_created',
                'date_modified',
            ),
        }),
    )

    def display_user_uuid(self, obj):
        """Exposes the immutable UUID token of the content creator."""
        return obj.created_by_id or "-"

    display_user_uuid.short_description = "Creator UUID Token"


@admin.register(DeltaDirectives)
class DeltaDirectivesAdmin(admin.ModelAdmin):
    """Management grid for AI directive and constraint configuration."""

    list_display = (
        'directive_name',
        'is_active',
        'display_user_uuid',
        'date_created',
        'date_modified',
    )
    search_fields = (
        'directive_name',
        'instructions',
        'created_by__username',
    )
    list_filter = (
        'is_active',
        'date_created',
        'date_modified',
    )
    readonly_fields = (
        'id',
        'display_user_uuid',
        'date_created',
        'date_modified',
    )
    ordering = ('directive_name',)
    list_select_related = ('created_by',)

    fieldsets = (
        ('Minion Core Identity', {
            'fields': (
                'id',
                'directive_name',
                'is_active',
            )
        }),
        ('Dense AI Prompt Instructions', {
            'fields': ('instructions',)
        }),
        ('Structured Parameter Boundaries & Rules', {
            'fields': (
                'constraints',
                'created_by',
                'display_user_uuid',
            )
        }),
        ('Record History', {
            'fields': (
                'date_created',
                'date_modified',
            ),
        }),
    )

    def display_user_uuid(self, obj):
        """Exposes the immutable UUID token of the author."""
        return obj.created_by_id or "-"

    display_user_uuid.short_description = "Author UUID Token"
# ======================================================================
# END: CONTENT_AND_DIRECTIVES_ADMIN (PATCH 2 OF 5)
# ======================================================================

# ======================================================================
# FILE: aurora/admin.py (PATCH 3 OF 5)
# START: NOTES_LEDGER_AND_REVIEW_ADMIN
# ======================================================================
@admin.register(DeltaNotesEntry)
class DeltaNotesEntryAdmin(admin.ModelAdmin):
    """Management grid for developer intentions and session logs."""

    list_display = (
        'user',
        'display_user_uuid',
        'short_text',
        'processed',
        'display_focus_time',
        'created_at',
        'updated_at',
    )
    search_fields = (
        'text',
        'user__username',
        'user__email',
    )
    list_filter = (
        'processed',
        'created_at',
        'updated_at',
        'user',
    )
    readonly_fields = (
        'display_user_uuid',
        'created_at',
        'updated_at',
    )
    ordering = ('-created_at',)
    list_select_related = ('user',)

    fieldsets = (
        ('Developer Context Anchor', {
            'fields': (
                'user',
                'display_user_uuid',
                'processed',
            )
        }),
        ('Active Intention / Task Blocks', {
            'fields': ('text',)
        }),
        ('🎛️ Session Focus Timer Metrics', {
            'fields': (
                'total_seconds_logged',
                'last_started_at',
            ),
        }),
        ('Record History', {
            'fields': (
                'created_at',
                'updated_at',
            ),
        }),
    )

    def display_user_uuid(self, obj):
        """Exposes the internal developer UUID string."""
        return obj.user_id or "-"

    display_user_uuid.short_description = "Developer UUID Token"

    def short_text(self, obj):
        """Truncates long logs for clean display rows."""
        return obj.text[:60] + "..." if len(obj.text) > 60 else obj.text

    short_text.short_description = "Logged Intention Statement"

    def display_focus_time(self, obj):
        """Translates raw logged seconds into a readable duration."""
        total_seconds = obj.total_seconds_logged or 0
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        return f"⏱️ {hours:02d}h {minutes:02d}m {seconds:02d}s"

    display_focus_time.short_description = "Total Accumulated Focus Time"


@admin.register(ChatLedgerEntry)
class ChatLedgerEntryAdmin(admin.ModelAdmin):
    """Read-oriented view of persisted Wu conversation history."""

    list_display = (
        'session_id',
        'role',
        'user',
        'short_text',
        'created_at',
    )
    search_fields = (
        'session_id',
        'text',
        'user__username',
        'user__email',
    )
    list_filter = (
        'role',
        'created_at',
        'user',
    )
    readonly_fields = (
        'id',
        'user',
        'session_id',
        'role',
        'text',
        'created_at',
    )
    ordering = ('-created_at',)
    list_select_related = ('user',)
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def short_text(self, obj):
        """Provides a compact preview of the persisted message."""
        normalized_text = ' '.join(obj.text.split())
        return (
            normalized_text[:80] + "..."
            if len(normalized_text) > 80
            else normalized_text
        )

    short_text.short_description = "Message Preview"


@admin.register(PendingCodeChange)
class PendingCodeChangeAdmin(admin.ModelAdmin):
    """Read-oriented inspection view for Wu code-review transactions."""

    list_display = (
        'file_path',
        'status',
        'user',
        'date_created',
        'date_reviewed',
        'date_applied',
    )
    search_fields = (
        'file_path',
        'original_sha256',
        'user__username',
        'user__email',
    )
    list_filter = (
        'status',
        'date_created',
        'date_reviewed',
        'date_applied',
        'user',
    )
    readonly_fields = (
        'id',
        'user',
        'file_path',
        'original_sha256',
        'original_content',
        'proposed_content',
        'status',
        'date_created',
        'date_reviewed',
        'date_applied',
    )
    ordering = ('-date_created',)
    list_select_related = ('user',)
    date_hierarchy = 'date_created'

    fieldsets = (
        ('Review Transaction', {
            'fields': (
                'id',
                'user',
                'file_path',
                'status',
                'original_sha256',
            ),
        }),
        ('Current Source Snapshot', {
            'fields': ('original_content',),
        }),
        ('Wu Proposed Replacement', {
            'fields': ('proposed_content',),
        }),
        ('Review Timeline', {
            'fields': (
                'date_created',
                'date_reviewed',
                'date_applied',
            ),
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
# ======================================================================
# END: NOTES_LEDGER_AND_REVIEW_ADMIN (PATCH 3 OF 5)
# ======================================================================

# ======================================================================
# FILE: aurora/admin.py (PATCH 4 OF 5)
# START: INITIATIVE_AND_PHASE_ADMIN
# ======================================================================
@admin.register(Initiative)
class InitiativeAdmin(admin.ModelAdmin):
    """Management view for top-level Aurora execution initiatives."""

    list_display = (
        'position',
        'title',
        'status',
        'created_by',
        'phase_count',
        'created_at',
        'updated_at',
        'completed_at',
    )
    search_fields = (
        'title',
        'description',
        'created_by__username',
        'created_by__email',
    )
    list_filter = (
        'status',
        'created_at',
        'updated_at',
        'completed_at',
        'created_by',
    )
    readonly_fields = (
        'created_at',
        'updated_at',
        'completed_at',
        'phase_count',
    )
    ordering = (
        'position',
        'created_at',
    )
    list_select_related = ('created_by',)

    fieldsets = (
        ('Initiative Identity', {
            'fields': (
                'title',
                'description',
            ),
        }),
        ('Execution State', {
            'fields': (
                'status',
                'position',
                'phase_count',
            ),
        }),
        ('Ownership', {
            'fields': ('created_by',),
        }),
        ('Lifecycle History', {
            'fields': (
                'created_at',
                'updated_at',
                'completed_at',
            ),
        }),
    )

    def phase_count(self, obj):
        """Displays the number of phases assigned to the initiative."""
        return obj.phases.count()

    phase_count.short_description = "Phases"


@admin.register(Phase)
class PhaseAdmin(admin.ModelAdmin):
    """Management view for ordered initiative milestones."""

    list_display = (
        'position',
        'title',
        'initiative',
        'status',
        'step_count',
        'created_at',
        'updated_at',
        'completed_at',
    )
    search_fields = (
        'title',
        'description',
        'initiative__title',
    )
    list_filter = (
        'status',
        'initiative',
        'created_at',
        'updated_at',
        'completed_at',
    )
    readonly_fields = (
        'created_at',
        'updated_at',
        'completed_at',
        'step_count',
    )
    ordering = (
        'initiative__position',
        'initiative',
        'position',
        'created_at',
    )
    list_select_related = ('initiative',)

    fieldsets = (
        ('Phase Identity', {
            'fields': (
                'initiative',
                'title',
                'description',
            ),
        }),
        ('Execution State', {
            'fields': (
                'status',
                'position',
                'step_count',
            ),
        }),
        ('Lifecycle History', {
            'fields': (
                'created_at',
                'updated_at',
                'completed_at',
            ),
        }),
    )

    def step_count(self, obj):
        """Displays the number of implementation steps in the phase."""
        return obj.steps.count()

    step_count.short_description = "Steps"
# ======================================================================
# END: INITIATIVE_AND_PHASE_ADMIN (PATCH 4 OF 5)
# ======================================================================

# ======================================================================
# FILE: aurora/admin.py (PATCH 5 OF 5)
# START: STEP_ADMIN
# ======================================================================
@admin.register(Step)
class StepAdmin(admin.ModelAdmin):
    """Management view for individual implementation steps."""

    list_display = (
        'position',
        'title',
        'phase',
        'initiative',
        'status',
        'estimated_minutes',
        'estimate_confidence',
        'validated_by',
        'created_at',
        'updated_at',
        'completed_at',
    )
    search_fields = (
        'title',
        'description',
        'validation_description',
        'validation_notes',
        'phase__title',
        'phase__initiative__title',
        'validated_by__username',
        'validated_by__email',
    )
    list_filter = (
        'status',
        'estimate_confidence',
        'phase__initiative',
        'phase',
        'validated_by',
        'created_at',
        'updated_at',
        'completed_at',
    )
    readonly_fields = (
        'created_at',
        'updated_at',
        'completed_at',
        'initiative',
    )
    ordering = (
        'phase__initiative__position',
        'phase__initiative',
        'phase__position',
        'phase',
        'position',
        'created_at',
    )
    list_select_related = (
        'phase',
        'phase__initiative',
        'validated_by',
    )

    fieldsets = (
        ('Step Identity', {
            'fields': (
                'phase',
                'initiative',
                'title',
                'description',
            ),
        }),
        ('Execution State', {
            'fields': (
                'status',
                'position',
            ),
        }),
        ('Effort Estimate', {
            'fields': (
                'estimated_minutes',
                'estimate_confidence',
            ),
        }),
        ('Validation', {
            'fields': (
                'validation_description',
                'validated_by',
                'validation_notes',
            ),
        }),
        ('Lifecycle History', {
            'fields': (
                'created_at',
                'updated_at',
                'completed_at',
            ),
        }),
    )

    def initiative(self, obj):
        """Displays the initiative containing the selected step."""
        return obj.phase.initiative

    initiative.short_description = "Initiative"
    initiative.admin_order_field = 'phase__initiative__title'
# ======================================================================
# END: STEP_ADMIN (PATCH 5 OF 5)
# ======================================================================