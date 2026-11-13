import unittest

from app.agents import list_agents, route_agent
from app.brain import build_system_prompt


class MikeWillAgentTests(unittest.TestCase):
    def test_mike_and_will_are_active_children_of_eleven(self):
        agents = {item["name"]: item for item in list_agents()}
        for name in ("mike", "will"):
            self.assertEqual(agents[name]["parent"], "eleven")
            self.assertEqual(agents[name]["status"], "active")

    def test_mike_drive_and_will_career_routing(self):
        cases = {
            "Find my Google Drive files": "mike",
            "Search my Drive for the project report": "mike",
            "Find Java internships": "will",
            "Improve my ATS resume": "will",
            "Prepare me for a technical interview": "will",
            "Help with freelancing proposals": "will",
        }
        for message, expected in cases.items():
            with self.subTest(message=message):
                self.assertEqual(route_agent(message), expected)

    def test_mike_prompt_is_read_only_and_discloses_connection_requirement(self):
        prompt = build_system_prompt("mike", [])
        self.assertIn("read-only", prompt.lower())
        self.assertIn("never pretend", prompt.lower())
        self.assertIn("Google Drive", prompt)

    def test_will_prompt_covers_career_and_truthful_job_search(self):
        prompt = build_system_prompt("will", [])
        for phrase in ("ATS-friendly", "interview preparation", "Never invent", "application"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.lower(), prompt.lower())


if __name__ == "__main__":
    unittest.main()
