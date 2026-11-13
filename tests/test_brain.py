import unittest

from app.agents import list_agents, route_agent
from app.brain import (
    search_dustin_web,
    build_lucas_synthesis_prompt,
    build_specialist_prompt,
    build_system_prompt,
)
from app.delegation import create_lucas_plan
from app.config import Settings


class DustinSearchTests(unittest.IsolatedAsyncioTestCase):
    async def test_live_search_is_not_attempted_without_provider_key(self):
        settings = Settings(tavily_api_key=None)
        self.assertEqual(await search_dustin_web(settings, "latest AI research"), [])


class AgentHierarchyTests(unittest.TestCase):
    def test_department_routing(self):
        cases = {
            "Plan my workout and diet": "max",
            "Log my meals and calculate my macros": "max",
            "I ate two eggs and oats for breakfast": "max",
            "I weighed 72 kilograms this morning": "max",
            "Analyse my weekly weight trend": "max",
            "Suggest a fat loss meal plan": "max",
            "Find jobs on LinkedIn and improve my resume": "will",
            "Find a PDF in Google Drive": "mike",
            "Research the best cloud certifications": "dustin",
            "Research the latest AI tools and compare reliable sources": "dustin",
            "Find sources and fact-check this claim": "dustin",
            "Fix this Flutter bug": "lucas",
            "Build a Vue.js frontend": "lucas",
            "Create a responsive Bootstrap page": "lucas",
            "Build an Android app in Kotlin": "lucas",
            "Create a PHP Laravel API": "lucas",
            "Optimize a MongoDB database": "lucas",
            "Write Playwright end-to-end tests": "lucas",
            "Build a C++ service": "lucas",
            "Create a SvelteKit website": "lucas",
            "Build a React Native app": "lucas",
            "Create a SwiftUI iOS app": "lucas",
            "Build a Rust microservice": "lucas",
            "Create a GitHub Actions CI/CD pipeline": "lucas",
            "Deploy my app with Docker and Nginx": "lucas",
            "Hello Eleven": "eleven",
            "Dustin": "dustin",
            "Max": "max",
        }
        for message, expected in cases.items():
            with self.subTest(message=message):
                self.assertEqual(route_agent(message), expected)

    def test_lucas_has_six_equal_level_specialists(self):
        agents = {item["name"]: item for item in list_agents()}
        self.assertEqual(agents["lucas"]["parent"], "eleven")
        specialist_names = {"frontend", "mobile", "backend", "database", "testing", "devops"}
        self.assertEqual(
            {name for name, item in agents.items() if item["parent"] == "lucas"},
            specialist_names,
        )

    def test_lucas_has_six_equal_level_specialists_including_devops(self):
        agents = {item["name"]: item for item in list_agents()}
        expected = {"frontend", "mobile", "backend", "database", "testing", "devops"}
        self.assertEqual(
            {name for name, item in agents.items() if item["parent"] == "lucas"},
            expected,
        )
        self.assertTrue({"github_actions", "docker", "terraform", "monitoring", "rollback"}.issubset(set(agents["devops"]["capabilities"])))

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

    def test_mobile_backend_database_testing_have_broad_domain_skills(self):
        agents = {item["name"]: item for item in list_agents()}
        expected = {
            "mobile": {
                "flutter", "react_native", "kotlin", "swift", "swiftui",
                "dotnet_maui", "ionic", "appium", "play_store_release",
            },
            "backend": {
                "java", "spring_boot", "python", "django", "fastapi", "php",
                "laravel", "aspnet", "c", "cpp", "nodejs", "golang",
                "microservices", "oauth2", "docker",
            },
            "database": {
                "sql", "postgresql", "mysql", "sql_server", "oracle_database",
                "sqlite", "mongodb", "redis", "cassandra", "dynamodb",
                "firebase", "schema_design", "replication", "backup",
            },
            "testing": {
                "manual_testing", "unit_testing", "integration_testing",
                "end_to_end_testing", "api_testing", "performance_testing",
                "security_testing", "selenium", "playwright", "cypress",
                "appium", "pytest", "junit", "jmeter",
            },
        }
        for agent_name, required in expected.items():
            with self.subTest(agent=agent_name):
                self.assertEqual(agents[agent_name]["parent"], "lucas")
                self.assertTrue(required.issubset(set(agents[agent_name]["capabilities"])))

    def test_all_five_personal_agents_are_present(self):
        agents = {item["name"]: item for item in list_agents()}
        self.assertEqual(
            {name for name in ("max", "will", "mike", "dustin", "lucas")
             if agents[name]["parent"] == "eleven"},
            {"max", "will", "mike", "dustin", "lucas"},
        )

    def test_dustin_is_elevens_personal_research_specialist(self):
        agents = {item["name"]: item for item in list_agents()}
        self.assertEqual(agents["dustin"]["parent"], "eleven")
        self.assertTrue({
            "web_search", "source_discovery", "citations", "fact_check",
            "evidence_synthesis", "comparisons",
        }.issubset(set(agents["dustin"]["capabilities"])))
        prompt = build_system_prompt("dustin", [])
        self.assertIn("never invent", prompt.lower())
        self.assertIn("primary", prompt.lower())

    def test_max_prompt_has_health_safety_and_tracking_scope(self):
        prompt = build_system_prompt("max", [])
        self.assertIn("weekly weight averages", prompt)
        self.assertIn("crash diets", prompt)
        self.assertIn("registered dietitian", prompt)

    def test_specialist_prompt_contains_role_and_memory(self):
        prompt = build_system_prompt("lucas", [{"content": "Prefers Hindi"}])
        self.assertIn("head of the Coding Department", prompt)
        self.assertIn("Prefers Hindi", prompt)

    def test_devops_tasks_route_to_devops_and_testing(self):
        for task in ("Create a GitHub Actions CI/CD pipeline", "Deploy a Docker Compose app", "Add Terraform infrastructure and monitoring"):
            with self.subTest(task=task):
                self.assertEqual(create_lucas_plan(task)["specialists"], ["devops", "testing"])

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

    def test_react_native_is_not_misrouted_to_frontend(self):
        plan = create_lucas_plan("Build a React Native mobile app")
        self.assertEqual(plan["specialists"], ["mobile", "testing"])

    def test_sveltekit_and_rust_tasks_select_the_correct_specialist(self):
        frontend = create_lucas_plan("Build a SvelteKit website")
        backend = create_lucas_plan("Create a Rust backend service")
        self.assertEqual(frontend["specialists"], ["frontend", "testing"])
        self.assertEqual(backend["specialists"], ["backend", "testing"])

    def test_specialist_prompts_are_domain_specific(self):
        self.assertIn("Flutter/Dart", build_specialist_prompt("mobile", "Build an app"))
        self.assertIn("PostgreSQL", build_specialist_prompt("database", "Tune queries"))
        self.assertIn("security", build_specialist_prompt("testing", "Review API"))

    def test_lucas_synthesis_enforces_execution_boundary(self):
        prompt = build_lucas_synthesis_prompt(
            "Build a React page",
            {"frontend": "Suggested component code."},
            "Proposed tests: responsive layout and keyboard navigation.",
        )
        self.assertIn("You have not executed shell commands", prompt)
        self.assertIn("Testing Agent review", prompt)
        self.assertIn("Suggested component code.", prompt)


if __name__ == "__main__":
    unittest.main()
