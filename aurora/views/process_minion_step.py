import os
import shutil
import subprocess
from django.views.generic import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from aurora.models import AutomatedBuildStep
from .automation_dashboard import AutomatedBuildStepForm
from aurora.utils.file_mutator import apply_file_mutation

class ProcessMinionStepView(View):
    """
    Handles live form code modifications, executes file mutations,
    and captures exact terminal traceback logs for visibility.
    """
    def post(self, request, *args, **kwargs):
        step_id = self.kwargs.get('step_id')
        step = get_object_or_404(AutomatedBuildStep, id=step_id)
        
        form = AutomatedBuildStepForm(request.POST, instance=step)
        if form.is_valid():
            step = form.save(commit=False)
            step.approval_status = 'APPROVED'
            step.save()
            
            mutation_success = apply_file_mutation(
                target_file_path=step.target_file_path,
                code_payload=step.code_payload,
                anchor_signature=step.anchor_signature
            )
            
            if not mutation_success:
                step.execution_logs = f"[CRITICAL ERROR]: Failed to find anchor token signature: '{step.anchor_signature}'\n"
                step.save()
                messages.error(request, "Failed to resolve insertion anchor. See console details.")
                return redirect(reverse('aurora:pipeline_dashboard', kwargs={'feature_name': step.feature_name}))

            try:
                result = subprocess.run(
                    step.verification_command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=20
                )
                
                output_log = f"$ {step.verification_command}\n"
                if result.stdout:
                    output_log += f"[STDOUT]\n{result.stdout}\n"
                if result.stderr:
                    output_log += f"[STDERR (Tracebacks)]\n{result.stderr}\n"
                
                step.execution_logs = output_log
                
                if result.returncode == step.expected_exit_code:
                    step.is_executed = True
                    messages.success(request, f"Step {step.step_order} verified successfully!")
                    
                    backup_path = f"{step.target_file_path}.bak"
                    if os.path.exists(backup_path):
                        os.remove(backup_path)
                else:
                    step.is_executed = False
                    messages.error(request, f"Subprocess validation check failed with exit code {result.returncode}.")
                    
            except subprocess.TimeoutExpired:
                step.execution_logs = f"[TIMEOUT CRITICAL ERROR]: Shell command timed out.\n"
                step.is_executed = False
                messages.error(request, "Task execution timed out.")
            except Exception as e:
                step.execution_logs = f"[SYSTEM FAULT EXCEPTION]:\n{str(e)}\n"
                step.is_executed = False
                messages.error(request, "A system file handling error occurred.")
            
            step.save()
        else:
            messages.error(request, "Invalid configuration variables found in form.")

        return redirect(reverse('aurora:pipeline_dashboard', kwargs={'feature_name': step.feature_name}))


class RollbackMinionStepView(View):
    """
    Instantly wipes out experimental code mutations and completely restores 
    the file system using pristine background .bak files.
    """
    def post(self, request, *args, **kwargs):
        step_id = self.kwargs.get('step_id')
        step = get_object_or_404(AutomatedBuildStep, id=step_id)
        backup_path = f"{step.target_file_path}.bak"
        
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, step.target_file_path)
            os.remove(backup_path)
            step.execution_logs = "[SYSTEM CONTROL]: Rollback executed. File completely restored.\n"
            messages.info(request, f"Step {step.step_order} changes discarded.")
        else:
            if os.path.exists(step.target_file_path) and step.stage == 'BUILD_HTML':
                os.remove(step.target_file_path)
                step.execution_logs = "[SYSTEM CONTROL]: New file deleted.\n"
                messages.info(request, "Newly created file removed successfully.")
            else:
                messages.warning(request, "No active backup file trace found to restore.")
                
        step.approval_status = 'PENDING_REVIEW'
        step.is_executed = False
        step.save()
        
        return redirect(reverse('aurora:pipeline_dashboard', kwargs={'feature_name': step.feature_name}))


class StepBackwardNavigationView(View):
    """
    Manually rolls the pipeline sequence backward by one step,
    allowing operators to re-review or overwrite prior code payloads.
    """
    def post(self, request, *args, **kwargs):
        current_step_id = self.kwargs.get('step_id')
        current_step = get_object_or_404(AutomatedBuildStep, id=current_step_id)
        
        previous_step = AutomatedBuildStep.objects.filter(
            feature_name=current_step.feature_name,
            step_order__lt=current_step.step_order
        ).order_by('-step_order').first()
        
        if previous_step:
            AutomatedBuildStep.objects.filter(
                feature_name=current_step.feature_name,
                step_order__gte=previous_step.step_order
            ).update(is_executed=False, approval_status='PENDING_REVIEW')
            
            messages.info(request, f"Moved backward to Step {previous_step.step_order}.")
        else:
            messages.warning(request, "You are already at the first step of this pipeline.")
            
        return redirect(reverse('aurora:pipeline_dashboard', kwargs={'feature_name': current_step.feature_name}))
