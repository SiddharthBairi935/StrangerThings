import unittest

from app.agents import list_agents, route_agent
from app.brain import build_system_prompt
from app.delegation import create_lucas_plan


class AgentHierarchyTests(unittest.TestCase):
    def test_department_routing(self):
        cases = {
            "Plan my workout and diet": "max",
            "Find jobs on LinkedIn and improve my resume": "will",
            "Find a PDF in Google Drive": "mike",
            "Research the best cloud certifications": "dustin",
            "Fix this Flutter bug": "lucas",
            "Build a Vue.js frontend": "lucas",
            "Create a responsive Bootstrap page": "lucas",
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

    def test_frontend_agent_has_broad_frontend_capabilities(self):
        agents = {item["name"]: item for item in list_agents()}
        frontend = agents["frontend"]
        self.assertEqual(frontend["parent"], "lucas")
        capabilities = set(frontend["capabilities"])
        expected = {
            "html5", "css3", "javascript", "typescript", "bootstrap", "tailwind_css",
            "react", "nextjs", "angular", "vue", "svelte", "nuxt",
            "responsive_design", "accessibility", "figma_to_code",
            "redux_toolkit", "material_ui", "graphql", "playwright",
            "performance_optimization",
        }
        self.assertTrue(expected.issubset(capabilities))

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

    def test_flutter_task_routes_to_mobile_and_testing(self):
        plan = create_lucas_plan("Fix the Flutter dashboard UI and test the screen")
        self.assertEqual(plan["specialists"], ["mobile", "testing"])
        self.assertFalse(plan["execution_started"])
        self.assertEqual(plan["status"], "planned")

    def test_full_stack_task_routes_to_multiple_specialists(self):
        plan = create_lucas_plan(
            "Build a React frontend with FastAPI backend and PostgreSQL database"
        )
        self.assertEqual(
            plan["specialists"], ["frontend", "backend", "database", "testing"]
        )

    def test_generic_task_still_includes_testing(self):
        plan = create_lucas_plan("Review this software project")
        self.assertEqual(plan["specialists"], ["backend", "testing"])


if __name__ == "__main__":
    unittest.main()
