import unittest

from app.agents import list_agents, route_agent
from app.brain import build_system_prompt


class AgentHierarchyTests(unittest.TestCase):
    def test_department_routing(self):
        cases = {
            "Plan my workout and diet": "max",
            "Find jobs on LinkedIn and improve my resume": "will",
            "Find a PDF in Google Drive": "mike",
            "Research the best cloud certifications": "dustin",
            "Fix this Flutter bug": "lucas",
            "Hello Eleven": "eleven",
        }
        for message, expected in cases.items():
            with self.subTest(message=message):
                self.assertEqual(route_agent(message), expected)

    def test_lucas_has_five_equal_level_specialists(self):
        agents = {item["name"]: item for item in list_agents()}
        self.assertEqual(agents["lucas"]["parent"], "eleven")
        specialist_names = {"frontend", "mobile", "backend", "database", "testing"}
        self.assertEqual(
            {name for name, item in agents.items() if item["parent"] == "lucas"},
            specialist_names,
        )

    def test_all_five_personal_agents_are_present(self):
        agents = {item["name"]: item for item in list_agents()}
        self.assertEqual(
            {name for name in ("max", "will", "mike", "dustin", "lucas")
             if agents[name]["parent"] == "eleven"},
            {"max", "will", "mike", "dustin", "lucas"},
        )

    def test_specialist_prompt_contains_role_and_memory(self):
        prompt = build_system_prompt("lucas", [{"content": "Prefers Hindi"}])
        self.assertIn("head of the Coding Department", prompt)
        self.assertIn("Prefers Hindi", prompt)


if __name__ == "__main__":
    unittest.main()
