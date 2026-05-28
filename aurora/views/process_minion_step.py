import subprocess
from django.views.generic import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from aurora.models import AutomatedBuildStep
from .automation_dashboard import AutomatedBuildStepForm

class ProcessMinionStepView(View):
    """
    Saves human text-area code modifications, authorizes the assigned 
    Minion worker to execute file mutations, and logs tracking telemetry.
    """
    
    def post(self, request, *args, **kwargs):
        step_id = self.kwargs.get('step_id')
        step = get_object_or_404(AutomatedBuildStep, id=step_id)
        
        # Bind submitted form data to verify code payload modifications
        form = AutomatedBuildStepForm(request.POST, instance=step)
        
        if form.is_valid():
            # 1. Save all human adjustments and toggle approval status
            step = form.save(commit=False)
            step.approval_status = 'APPROVED'
            step.save()
            
            # 2. Trigger the Minion File-Mutation Pipeline Execution
            try:
                # Execute the verification command via sandboxed subprocess shell
                result = subprocess.run(
                    step.verification_command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30  # Safety timeout threshold to prevent hangs
                )
                
                # Combine stdout and stderr text blocks into your database tracking log
                output_log = f"$ {step.verification_command}\n"
                if result.stdout:
                    output_log += f"[STDOUT]\n{result.stdout}\n"
                if result.stderr:
                    output_log += f"[STDERR]\n{result.stderr}\n"
                    
                step.execution_logs = output_log
                
                # 3. Assess the Minion's Exit Code Target
                if result.returncode == step.expected_exit_code:
                    step.is_executed = True
                    messages.success(
                        request, 
                        f"Minion [{step.assigned_minion}] executed Step {step.step_order} successfully!"
                    )
                else:
                    messages.error(
                        request, 
                        f"Validation error! Exit code {result.returncode} did not match expected {step.expected_exit_code}."
                    )
                    
            except subprocess.TimeoutExpired:
                step.execution_logs = f"Error: Command timed out after 30 seconds."
                messages.error(request, "The Minion task execution timed out.")
            except Exception as e:
                step.execution_logs = f"System Error Exception occurred:\n{str(e)}"
                messages.error(request, f"An unexpected execution engine fault occurred: {str(e)}")
            
            # Save the execution run records back to the PostgreSQL table rows
            step.save()
            
        else:
            messages.error(request, "Invalid configuration values detected in your plan adjustments.")

        # Redirect directly back to your dashboard viewport frame
        return redirect(reverse('aurora:pipeline_dashboard', kwargs={'feature_name': step.feature_name}))
