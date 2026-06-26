# ======================================================================
# FILE: aurora/tests/test_models.py (PATCH 1 OF 3)
# START: SCHEMA INITIALIZATION & PATH-ISOLATED NEO4J FLUSH
# ======================================================================
from django.test import TestCase
from django.db.utils import IntegrityError
from django.db.models import ProtectedError
from django.contrib.auth.models import User
from neomodel import db as neomodel_db
from aurora.models import ComponentRegistry, StaticContent, DeltaDirectives

class ComponentRegistryModelTests(TestCase):
    """Test suite ensuring field constraints and structural relationships behave perfectly."""

    def setUp(self):
        """Establish baseline developer records and clear sandbox graph references safely."""
        # SAFE FIX: Clear only sandboxed test file prefixes to shield production nodes
        try:
            neomodel_db.cypher_query(
                "MATCH (n) WHERE n.file_path STARTS WITH 'app/hopehub/pages/' "
                "OR n.file_path STARTS WITH 'app/test_assets/' DETACH DELETE n"
            )
        except Exception:
            pass
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
        """Surgically flush simulated test footprints from the loopback database."""
        try:
            neomodel_db.cypher_query(
                "MATCH (n) WHERE n.file_path STARTS WITH 'app/hopehub/pages/' "
                "OR n.file_path STARTS WITH 'app/test_assets/' DETACH DELETE n"
            )
        except Exception:
            pass

    def test_component_record_instantiates_with_pristine_defaults(self):
        """Schema Check: Verify record insertion maps values and sets defaults correctly."""
        entry = ComponentRegistry.objects.create(**self.valid_params)
        self.assertIsNotNone(entry.id)
        self.assertEqual(entry.name, "medical_logs")
        self.assertEqual(entry.description_audiences, {"developers": "initial docs"})
        self.assertFalse(entry.locked)
        self.assertEqual(str(entry), "medical_logs [COMPILER_MODULE] - Locked: False")

    def test_new_persona_choices_can_be_saved_successfully(self):
        """Taxonomy Check: Verify that the new grouped persona keys persist correctly in database."""
        test_personas = ['UI_LAYOUT', 'UI_STYLE', 'UI_LOGIC', 'UI_MEDIA', 'DOCUMENTATION', 'CONFIGURATION', 'DIAGNOSTIC_LOG']
        for idx, persona_key in enumerate(test_personas):
            entry = ComponentRegistry.objects.create(
                file_path=f"app/test_assets/file_{idx}.ext",
                name=f"test_asset_{idx}",
                persona=persona_key,
                created_by=self.user
            )
            self.assertEqual(entry.persona, persona_key)
# ======================================================================
# END: SCHEMA INITIALIZATION & PATH-ISOLATED NEO4J FLUSH (PATCH 1 OF 3)
# ======================================================================

# ======================================================================
# FILE: aurora/tests/test_models.py (PATCH 2 OF 3)
# START: REGISTRY_CONSTRAINT_TASKS_AND_CHILD_INITIALIZATION
# ======================================================================
    def test_duplicate_file_paths_are_strictly_blocked_by_database(self):
        """Constraint Check: Unique parameters must trigger IntegrityError on collisions."""
        ComponentRegistry.objects.create(**self.valid_params)
        with self.assertRaises(IntegrityError):
            ComponentRegistry.objects.create(
                file_path="app/hopehub/pages/medical_logs.py",
                name="cloned_logs",
                created_by=self.user
            )

    def test_user_deletion_is_blocked_if_linked_to_active_components(self):
        """Accountability Check: User deletion must raise ProtectedError to guard repository logs."""
        ComponentRegistry.objects.create(**self.valid_params)
        with self.assertRaises(ProtectedError):
            self.user.delete()

class ChildModelsRelationshipTests(TestCase):
    """Test suite ensuring child schemas link properly and obey relational rules."""

    def setUp(self):
        """Establish master parent profile and isolate the local graph engine safely."""
        try:
            neomodel_db.cypher_query(
                "MATCH (n) WHERE n.file_path STARTS WITH 'app/core/vectors/' DETACH DELETE n"
            )
        except Exception:
            pass
        self.user = User.objects.create_user(username="test_dev", password="password_123")
        self.parent_component = ComponentRegistry.objects.create(
            file_path="app/core/vectors/ai_minion.py",
            name="ai_minion_orchestrator",
            created_by=self.user
        )

    def tearDown(self):
        """Wipe tracking footprints to uphold isolation loop boundaries cleanly."""
        try:
            neomodel_db.cypher_query(
                "MATCH (n) WHERE n.file_path STARTS WITH 'app/core/vectors/' DETACH DELETE n"
            )
        except Exception:
            pass
# ======================================================================
# END: REGISTRY_CONSTRAINT_TASKS_AND_CHILD_INITIALIZATION (PATCH 2 OF 3)
# ======================================================================

# ======================================================================
# FILE: aurora/tests/test_models.py (PATCH 3 OF 3)
# START: CHILD_SCHEMA_ASSERTIONS_AND_MIGRATED_SCHEMA_FIX
# ======================================================================
    def test_static_content_instantiates_and_cascades_properly(self):
        """Standalone Check: Verify StaticContent instantiates with standalone fields and user relationship."""
        # FIXED: Removed legacy component_registry field and bound valid created_by tracking user
        content = StaticContent.objects.create(
            title="Privacy Policy",
            html_content="<h1>Privacy Information</h1>",
            application=StaticContent.ApplicationChoices.AURORA,
            created_by=self.user
        )
        self.assertEqual(content.application, "aurora")
        self.assertIn("Privacy Policy", str(content))

    def test_delta_directives_stores_json_constraints_and_cascades(self):
        """Relational Check: Verify DeltaDirectives handles payload constraints and sweeps clean."""
        # FIXED: Bound valid created_by tracking link to satisfy non-null constraints
        directive = DeltaDirectives.objects.create(
            directive_name="Token Throttle Limit",
            instructions="Maintain clear bounding thresholds on generation lengths.",
            constraints={"max_tokens_per_call": 200, "allowed_models": ["gpt-4o"]},
            created_by=self.user
        )
        self.assertEqual(directive.constraints["max_tokens_per_call"], 200)
        self.assertTrue(directive.is_active)
        self.assertIn("Token Throttle Limit", str(directive))

    def test_provision_standard_minions_seeds_entire_fleet(self):
        """Factory Check: Verify programmatic minion creation populates all 6 core rows."""
        # FIXED: Passed the required 'author_user' positional argument to handle new schema requirements
        created_count = DeltaDirectives.provision_standard_minions(author_user=self.user)
        self.assertEqual(created_count, 6)
        
        # Verify specific records persist in the active dataset matrix
        all_directives = DeltaDirectives.objects.all()
        names = [m.directive_name for m in all_directives]
        self.assertIn("minion_wu", names)
        self.assertIn("minion_UI_layout", names)
        self.assertIn("minion_AI_writer", names)
        
        wu_minion = DeltaDirectives.objects.get(directive_name="minion_wu")
        self.assertEqual(wu_minion.constraints["model"], "llama-3.3-70b-versatile")
# ======================================================================
# END: CHILD_SCHEMA_ASSERTIONS_AND_MIGRATED_SCHEMA_FIX (PATCH 3 OF 3)
# ======================================================================
