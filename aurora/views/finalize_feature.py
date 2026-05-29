from django.views.generic import View
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from aurora.models import AutomatedBuildStep

class FinalizeFeatureView(View):
    """
    Handles the Two-Part Validation Gate 2.
    Validates overall pipeline success and closes out the active feature pipeline
    upon human visual confirmation.
    """
    def post(self, request, *args, **kwargs):
        feature_name = self.kwargs.get('feature_name')

        # 1. Fetch all tracking steps associated with this specific feature scope
        pipeline_steps = AutomatedBuildStep.objects.filter(feature_name=feature_name)
        if not pipeline_steps.exists():
            messages.error(request, f"No automation pipeline records found for feature: '{feature_name}'.")
            return redirect(reverse('aurora:aurora_dashboard'))

        # 2. Strict Safety Guard: Verify no unexecuted steps remain in the sequence
        unexecuted_steps = pipeline_steps.filter(is_executed=False)
        if unexecuted_steps.exists():
            first_pending = unexecuted_steps.order_by('step_order').first()
            messages.error(
                request, 
                f"Cannot finalize feature. Step {first_pending.step_order} has not been completed by its minion."
            )
            return redirect(reverse('aurora:pipeline_dashboard', kwargs={'feature_name': feature_name}))

        # 3. Success State execution: Lock down the records and seal history logs
        final_step = pipeline_steps.order_by('-step_order').first()
        final_step.execution_logs += "\n[SYSTEM SIGNAL]: Two-Part Validation Complete. Human Operator signed off on visual feature rendering.\n"
        final_step.save()

        # 4. Notify operator and clear active minion context registries
        messages.success(
            request, 
            f"Deployment Blueprint Confirmed! Feature '{feature_name}' has been successfully finalized."
        )

        # Corrected Target: Matches app_name='aurora' + name='aurora_dashboard'
        return redirect(reverse('aurora:aurora_dashboard'))
