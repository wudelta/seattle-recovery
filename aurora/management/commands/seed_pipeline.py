from django.core.management.base import BaseCommand
from aurora.models import AutomatedBuildStep

class Command(BaseCommand):
    help = "Instantly seeds the relational database with the 4 core TDD steps for 'under_construction_page'."

    def handle(self, *args, **options):
        feature = 'under_construction_page'
        AutomatedBuildStep.objects.filter(feature_name=feature).delete()

        step1_code = (
            "from django.test import TestCase\n"
            "from django.urls import reverse, exceptions\n\n"
            "class TestUnderConstructionView(TestCase):\n"
            "    def test_page_resolves_and_renders_successfully(self):\n"
            "        try:\n"
            "            target_url = reverse('under_construction')\n"
            "        except exceptions.NoReverseMatch:\n"
            "            self.fail(\"Routing namespace 'under_construction' does not exist yet.\")\n"
            "        response = self.client.get(target_url)\n"
            "        self.assertEqual(response.status_code, 200)\n"
            "        self.assertContains(response, 'FEATURE UNDER CONSTRUCTION')\n"
        )

        step2_code = (
            '{% extends "base.html" %}\n'
            '{% block content %}\n'
            '<div class="container py-5 text-center">\n'
            '    <div class="card border-warning shadow-lg p-5">\n'
            '        <h1 class="text-warning font-monospace fw-bold">FEATURE UNDER CONSTRUCTION</h1>\n'
            '        <p class="text-muted">Our automated minions are assembling this module block-by-block.</p>\n'
            '    </div>\n'
            '</div>\n'
            '{% endblock %}\n'
        )

        step3_code = (
            "from django.views.generic import TemplateView\n\n"
            "class UnderConstructionView(TemplateView):\n"
            "    template_name = 'hopehub/construction.html'\n"
        )

        step4_code = (
            "    path('under-construction/', views.UnderConstructionView.as_view(), name='under_construction'),"
        )

        steps_pool = [
            AutomatedBuildStep(
                feature_name=feature,
                step_order=1,
                stage='SETUP_TEST',
                title='Init TDD Validation Architecture',
                assigned_minion='Test-Architect Minion',
                target_file_path='hopehub/tests/test_views.py',
                code_payload=step1_code,
                anchor_signature='',
                verification_command='python manage.py test hopehub.tests.test_views',
                expected_exit_code=1,
                approval_status='PENDING_REVIEW'
            ),
            AutomatedBuildStep(
                feature_name=feature,
                step_order=2,
                stage='BUILD_HTML',
                title='Deploy Bootswatch Canvas',
                assigned_minion='Frontend Forge Minion',
                target_file_path='hopehub/templates/hopehub/construction.html',
                code_payload=step2_code,
                anchor_signature='',
                verification_command='test -f hopehub/templates/hopehub/construction.html',
                expected_exit_code=0,
                approval_status='PENDING_REVIEW'
            ),
            AutomatedBuildStep(
                feature_name=feature,
                step_order=3,
                stage='BUILD_VIEW',
                title='Compile View Module',
                assigned_minion='Logic-Engine Minion',
                target_file_path='hopehub/views/under_construction.py',
                code_payload=step3_code,
                anchor_signature='',
                verification_command='python manage.py check',
                expected_exit_code=0,
                approval_status='PENDING_REVIEW'
            ),
            AutomatedBuildStep(
                feature_name=feature,
                step_order=4,
                stage='BUILD_ROUTER',
                title='Register URL Declarations',
                assigned_minion='Network Routing Minion',
                target_file_path='hopehub/urls.py',
                code_payload=step4_code,
                anchor_signature='urlpatterns = [',
                verification_command='python manage.py test hopehub.tests.test_views',
                expected_exit_code=0,
                approval_status='PENDING_REVIEW'
            )
        ]

        AutomatedBuildStep.objects.bulk_create(steps_pool)
        self.stdout.write(self.style.SUCCESS(f"Successfully seeded 4-step framework matrix for '{feature}'!"))
