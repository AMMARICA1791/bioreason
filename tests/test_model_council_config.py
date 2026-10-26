"""Larger Inventor remains opt-in and never silently changes peer models."""
import unittest

from bioreason.council import MODEL_ROLES
from scripts.model_council import (
    MODEL_ID, OPTIONAL_INVENTOR_MODEL_ID, select_model_id
)


class CouncilRoleModelSelectionTests(unittest.TestCase):
    def test_default_is_identical_across_all_eight_roles(self):
        self.assertEqual(len(MODEL_ROLES), 8)
        self.assertEqual(
            {select_model_id(role) for role in MODEL_ROLES}, {MODEL_ID}
        )

    def test_only_inventor_is_routed_to_larger_pilot_model(self):
        assignments = {
            role: select_model_id(role, OPTIONAL_INVENTOR_MODEL_ID)
            for role in MODEL_ROLES
        }
        self.assertEqual(assignments["Inventor"], OPTIONAL_INVENTOR_MODEL_ID)
        self.assertEqual(
            {model for role, model in assignments.items() if role != "Inventor"},
            {MODEL_ID},
        )

    def test_reject_unknown_models_and_roles(self):
        with self.assertRaisesRegex(ValueError, "Unapproved"):
            select_model_id("Inventor", "unknown/download-me")
        with self.assertRaisesRegex(ValueError, "Unknown"):
            select_model_id("InventorAndCritic", OPTIONAL_INVENTOR_MODEL_ID)

    def test_pilot_uses_no_extra_model_for_other_roles(self):
        for role in MODEL_ROLES:
            if role != "Inventor":
                self.assertEqual(select_model_id(role, OPTIONAL_INVENTOR_MODEL_ID),
                                 MODEL_ID)


if __name__ == "__main__":
    unittest.main()
