# ======================================================================
# FILE: aurora/subsystems/planning/admin.py
# START: PLANNING_ADMIN_IMPORTS
# ======================================================================

from django.contrib import admin

from aurora.subsystems.planning.models import (
    Initiative,
    Phase,
    Project,
    Step,
)


# ======================================================================
# END: PLANNING_ADMIN_IMPORTS
# ======================================================================

# ======================================================================
# FILE: aurora/subsystems/planning/admin.py
# START: PROJECT_INITIATIVE_AND_PHASE_ADMIN
# ======================================================================
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Management view for Decision Engine projects."""

    list_display = (
        'position',
        'title',
        'status',
        'active',
        'created_by',
        'assigned_to',
        'initiative_count',
        'created_at',
        'updated_at',
        'completed_at',
    )
    search_fields = (
        'title',
        'slug',
        'description',
        'created_by__username',
        'created_by__email',
        'assigned_to__username',
        'assigned_to__email',
    )
    list_filter = (
        'status',
        'active',
        'created_by',
        'assigned_to',
        'created_at',
        'updated_at',
        'completed_at',
    )
    readonly_fields = (
        'id',
        'initiative_count',
        'created_at',
        'updated_at',
        'completed_at',
    )
    ordering = (
        'position',
        'created_at',
    )
    list_select_related = (
        'created_by',
        'assigned_to',
    )

    fieldsets = (
        ('Project Identity', {
            'fields': (
                'id',
                'title',
                'slug',
                'description',
                'color',
                'icon',
            ),
        }),
        ('Execution State', {
            'fields': (
                'status',
                'active',
                'position',
                'initiative_count',
            ),
        }),
        ('Responsibility', {
            'fields': (
                'created_by',
                'assigned_to',
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

    def initiative_count(self, obj):
        """Displays the number of initiatives belonging to the project."""
        return obj.initiatives.count()

    initiative_count.short_description = "Initiatives"


@admin.register(Initiative)
class InitiativeAdmin(admin.ModelAdmin):
    """Management view for ordered project initiatives."""

    list_display = (
        'position',
        'title',
        'project',
        'status',
        'created_by',
        'assigned_to',
        'phase_count',
        'created_at',
        'updated_at',
        'completed_at',
    )
    search_fields = (
        'title',
        'description',
        'project__title',
        'project__slug',
        'created_by__username',
        'created_by__email',
        'assigned_to__username',
        'assigned_to__email',
    )
    list_filter = (
        'status',
        'project',
        'created_by',
        'assigned_to',
        'created_at',
        'updated_at',
        'completed_at',
    )
    readonly_fields = (
        'id',
        'phase_count',
        'created_at',
        'updated_at',
        'completed_at',
    )
    ordering = (
        'project__position',
        'project',
        'position',
        'created_at',
    )
    list_select_related = (
        'project',
        'created_by',
        'assigned_to',
    )

    fieldsets = (
        ('Initiative Identity', {
            'fields': (
                'id',
                'project',
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
        ('Responsibility', {
            'fields': (
                'created_by',
                'assigned_to',
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

    def phase_count(self, obj):
        """Displays the number of phases assigned to the initiative."""
        return obj.phases.count()

    phase_count.short_description = "Phases"


@admin.register(Phase)
class PhaseAdmin(admin.ModelAdmin):
    """Management view for ordered initiative phases."""

    list_display = (
        'position',
        'title',
        'initiative',
        'project',
        'status',
        'created_by',
        'assigned_to',
        'step_count',
        'created_at',
        'updated_at',
        'completed_at',
    )
    search_fields = (
        'title',
        'description',
        'initiative__title',
        'initiative__project__title',
        'initiative__project__slug',
        'created_by__username',
        'created_by__email',
        'assigned_to__username',
        'assigned_to__email',
    )
    list_filter = (
        'status',
        'initiative__project',
        'initiative',
        'created_by',
        'assigned_to',
        'created_at',
        'updated_at',
        'completed_at',
    )
    readonly_fields = (
        'id',
        'project',
        'step_count',
        'created_at',
        'updated_at',
        'completed_at',
    )
    ordering = (
        'initiative__project__position',
        'initiative__project',
        'initiative__position',
        'initiative',
        'position',
        'created_at',
    )
    list_select_related = (
        'initiative',
        'initiative__project',
        'created_by',
        'assigned_to',
    )

    fieldsets = (
        ('Phase Identity', {
            'fields': (
                'id',
                'project',
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
        ('Responsibility', {
            'fields': (
                'created_by',
                'assigned_to',
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

    def project(self, obj):
        """Displays the project containing the selected phase."""
        return obj.initiative.project

    project.short_description = "Project"
    project.admin_order_field = 'initiative__project__title'

    def step_count(self, obj):
        """Displays the number of implementation steps in the phase."""
        return obj.steps.count()

    step_count.short_description = "Steps"
# ======================================================================
# END: PROJECT_INITIATIVE_AND_PHASE_ADMIN
# ======================================================================

# ======================================================================
# FILE: aurora/subsystems/planning/admin.py
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
        'project',
        'status',
        'assigned_to',
        'estimated_minutes',
        'estimate_confidence',
        'risk_level',
        'validated_by',
        'created_at',
        'updated_at',
        'completed_at',
    )
    search_fields = (
        'title',
        'description',
        'risk_description',
        'validation_description',
        'validation_notes',
        'phase__title',
        'phase__initiative__title',
        'phase__initiative__project__title',
        'phase__initiative__project__slug',
        'created_by__username',
        'created_by__email',
        'assigned_to__username',
        'assigned_to__email',
        'validated_by__username',
        'validated_by__email',
    )
    list_filter = (
        'status',
        'estimate_confidence',
        'risk_level',
        'phase__initiative__project',
        'phase__initiative',
        'phase',
        'created_by',
        'assigned_to',
        'validated_by',
        'created_at',
        'updated_at',
        'completed_at',
    )
    readonly_fields = (
        'id',
        'project',
        'initiative',
        'created_at',
        'updated_at',
        'completed_at',
    )
    ordering = (
        'phase__initiative__project__position',
        'phase__initiative__project',
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
        'phase__initiative__project',
        'created_by',
        'assigned_to',
        'validated_by',
    )

    fieldsets = (
        ('Step Identity', {
            'fields': (
                'id',
                'project',
                'initiative',
                'phase',
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
        ('Responsibility', {
            'fields': (
                'created_by',
                'assigned_to',
            ),
        }),
        ('Effort Estimate', {
            'fields': (
                'estimated_minutes',
                'estimate_confidence',
            ),
        }),
        ('Risk Assessment', {
            'fields': (
                'risk_level',
                'risk_description',
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

    def project(self, obj):
        """Displays the project containing the selected step."""
        return obj.phase.initiative.project

    project.short_description = "Project"
    project.admin_order_field = 'phase__initiative__project__title'

    def initiative(self, obj):
        """Displays the initiative containing the selected step."""
        return obj.phase.initiative

    initiative.short_description = "Initiative"
    initiative.admin_order_field = 'phase__initiative__title'
# ======================================================================
# END: STEP_ADMIN
# ======================================================================