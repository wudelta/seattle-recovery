# ======================================================================
# FILE: aurora/tests/test_models.py (PATCH 1 OF 2)
# START: SCHEMA INITIALIZATION & NEO4J ISOLATION FLUSH HANDSHAKE
# ======================================================================
from django.test import TestCase
from django.db.utils import IntegrityError
from django.db.models import ProtectedError
from django.contrib.auth.models import User
from neomodel import db as neomodel_db # Imported to execute direct cypher isolation flushes
from aurora.models import ComponentRegistry, StaticContent, DeltaDirectives

class ComponentRegistryModelTests(TestCase):
    """Test suite ensuring field constraints and structural relationships behave perfectly."""

    def setUp(self):
        """Establish baseline developer records and flush the local loopback graph container."""
        # DEFINITIVE FIX: Wipe out any graph residue from prior test execution runs
        neomodel_db.cypher_query("MATCH (n) DETACH DELETE n")
        self.user = User.objects.create_user(username="db_architect", password="password_xyz")
        self.valid_params = {
            "file_path": "app/hopehub/pages/medical_logs.py",
            "name": "medical_logs",
            "persona": "COMPILER_MODULE",
            "status": "ACTIVE",
            "visibility": "PRIVATE",
            "locked": False,
            "created_by": self.user,
            "description": "Critical clinic system tracker.",
            "description_audiences": {"developers": "initial docs"}
        }

    def tearDown(self):
        """Flush simulated graph footprints to maintain immaculate system isolation."""
        neomodel_db.cypher_query("MATCH (n) DETACH DELETE n")

    def test_component_record_instantiates_with_pristine_defaults(self):
        """Schema Check: Verify record insertion maps values and sets defaults correctly."""
        entry = ComponentRegistry.objects.create(**self.valid_params)
        self.assertIsNotNone(entry.id)
        self.assertEqual(entry.name, "medical_logs")
        self.assertEqual(entry.description_audiences, {"developers": "initial docs"})
        self.assertFalse(entry.locked)
        self.assertEqual(str(entry), "medical_logs [COMPILER_MODULE] - Locked: False")

    def test_duplicate_file_paths_are_strictly_blocked_by_database(self):
        """Constraint Check: Unique parameters must trigger IntegrityError on collisions."""
        ComponentRegistry.objects.create(**self.valid_params)
        # Attempt to insert an identical filepath record profile
        with self.assertRaises(IntegrityError):
            ComponentRegistry.objects.create(
                file_path="app/hopehub/pages/medical_logs.py",
                name="cloned_logs",
                created_by=self.user
            )

    def test_user_deletion_is_blocked_if_linked_to_active_components(self):
        """Accountability Check: User deletion must raise ProtectedError to guard repository logs."""
        ComponentRegistry.objects.create(**self.valid_params)
        # Attempt to delete the creator while their components are active
        with self.assertRaises(ProtectedError):
            self.user.delete()
# ======================================================================
# END: SCHEMA INITIALIZATION & NEO4J ISOLATION FLUSH HANDSHAKE (PATCH 1 OF 2)
# ======================================================================

# ======================================================================
# FILE: aurora/tests/test_models.py (PATCH 2 OF 2)
# START: CHILD_MODELS_RELATIONSHIP_AND_CONSTRAINTS_TESTS
# ======================================================================
class ChildModelsRelationshipTests(TestCase):
    """Test suite ensuring child schemas link properly and obey relational rules."""

    def setUp(self):
        """Establish master parent profile and isolate the local graph engine."""
        neomodel_db.cypher_query("MATCH (n) DETACH DELETE n")
        self.user = User.objects.create_user(username="test_dev", password="password_123")
        self.parent_component = ComponentRegistry.objects.create(
            file_path="app/core/vectors/ai_minion.py",
            name="ai_minion_orchestrator",
            created_by=self.user
        )

    def tearDown(self):
        """Wipe tracking footprints to uphold isolation loop boundaries."""
        neomodel_db.cypher_query("MATCH (n) DETACH DELETE n")

    def test_static_content_instantiates_and_cascades_properly(self):
        """Relational Check: Verify StaticContent lifecycle binds tightly to parent component."""
        content = StaticContent.objects.create(
            component_registry=self.parent_component,
            title="Privacy Policy",
            html_content="<h1>Privacy Information</h1>"
        )
        self.assertEqual(content.component_registry.name, "ai_minion_orchestrator")
        self.assertIn("Privacy Policy", str(content))

        # Cascading Deletion Check
        self.parent_component.delete()
        self.assertEqual(StaticContent.objects.count(), 0)

    def test_delta_directives_stores_json_constraints_and_cascades(self):
        """Relational Check: Verify DeltaDirectives handles payload constraints and sweeps clean."""
        directive = DeltaDirectives.objects.create(
            component_registry=self.parent_component,
            directive_name="Token Throttle Limit",
            instructions="Maintain clear bounding thresholds on generation lengths.",
            constraints={"max_tokens_per_call": 200, "allowed_models": ["gpt-4o"]}
        )
        self.assertEqual(directive.constraints["max_tokens_per_call"], 200)
        self.assertTrue(directive.is_active)
        self.assertIn("Token Throttle Limit", str(directive))

        # Cascading Deletion Check
        self.parent_component.delete()
        self.assertEqual(DeltaDirectives.objects.count(), 0)
# ======================================================================
# END: CHILD_MODELS_RELATIONSHIP_AND_CONSTRAINTS_TESTS (PATCH 2 OF 2)
# ======================================================================
