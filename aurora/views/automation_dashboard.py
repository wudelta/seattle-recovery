from django import forms
from django.views.generic import UpdateView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, Fieldset, Field

from aurora.models import AutomatedBuildStep

# 1. THE FORM COMPONENT DEFINITION
class AutomatedBuildStepForm(forms.ModelForm):
    class Meta:
        model = AutomatedBuildStep
        fields = [
            'feature_name', 'step_order', 'stage', 'title', 
            'target_file_path', 'code_payload', 'anchor_signature', 
            'verification_command', 'expected_exit_code', 'human_notes'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'automation-blueprint-form'
        
        self.helper.layout = Layout(
            Fieldset(
                '1. Structural Blueprint Data',
                Row(
                    Column('feature_name', css_class='form-group col-md-4 mb-3'),
                    Column('step_order', css_class='form-group col-md-4 mb-3'),
                    Column('stage', css_class='form-group col-md-4 mb-3'),
                    css_class='row'
                ),
                Row(
                    Column('title', css_class='form-group col-md-6 mb-3'),
                    Column('target_file_path', css_class='form-group col-md-6 mb-3'),
                    css_class='row'
                ),
            ),
            Fieldset(
                '2. Automation Payloads & Target Markers',
                Field('code_payload', rows="6", css_class='font-monospace mb-3', placeholder="# Code or HTML element syntax blocks..."),
                Field('anchor_signature', css_class='mb-3', placeholder="e.g., urlpatterns = ["),
            ),
            Fieldset(
                '3. Self-Verification Rules & Human Feedback Loop',
                Row(
                    Column('verification_command', css_class='form-group col-md-8 mb-3'),
                    Column('expected_exit_code', css_class='form-group col-md-4 mb-3'),
                    css_class='row'
                ),
                Field('human_notes', rows="2", placeholder="Log layout adjustments or rationale adjustments here..."),
            ),
            Submit('submit', '✅ APPROVE STEP & REFRESH WORKER PIPELINE', css_class='btn btn-success btn-lg mt-3 w-100')
        )


# 2. THE VIEW CONTROLLER DEFINITION
class AutomationDashboardView(UpdateView):
    model = AutomatedBuildStep
    form_class = AutomatedBuildStepForm  # Binds to the class declared right above
    template_name = 'aurora/automation_dashboard.html'
    context_object_name = 'active_step'

    def get_object(self, queryset=None):
        feature_name = self.kwargs.get('feature_name')
        active_step = AutomatedBuildStep.objects.filter(
            feature_name=feature_name,
            is_executed=False
        ).order_by('step_order').first()

        if not active_step:
            active_step = AutomatedBuildStep.objects.filter(
                feature_name=feature_name
            ).order_by('-step_order').first()

        return active_step

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        feature_name = self.kwargs.get('feature_name')
        
        pipeline_steps = AutomatedBuildStep.objects.filter(
            feature_name=feature_name
        ).order_by('step_order')

        all_steps_executed = not pipeline_steps.filter(is_executed=False).exists()

        context.update({
            'feature_name': feature_name,
            'pipeline_steps': pipeline_steps,
            'all_steps_executed': all_steps_executed,
            'pipeline_status': 'VALIDATION_STAGE' if all_steps_executed else 'RUNNING',
        })
        return context
