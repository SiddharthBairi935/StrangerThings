from dataclasses import dataclass


@dataclass(frozen=True)
class AgentInfo:
    name: str
    title: str
    description: str
    status: str
    parent: str | None = None
    capabilities: tuple[str, ...] = ()


# "active" means routing and specialist instructions exist in Eleven.
# It does not imply that external accounts or tools are connected.
AGENTS: tuple[AgentInfo, ...] = (
    AgentInfo("eleven", "Eleven (11) / L", "Main assistant, central brain, task planner, and coordinator for every department.", "active", None, ("chat", "planning", "delegation", "coordination")),
    AgentInfo("max", "Max", "Personal health and fitness coach: food logs, nutrition estimates, meal planning, workouts, activity, weight trends, measurements, recovery, and progress. Not a medical diagnostician.", "active", "eleven", ("diet", "nutrition", "food_logging", "calorie_estimates", "macros", "meal_planning", "fitness", "workouts", "exercise_tracking", "weight_tracking", "body_measurements", "progress", "recovery", "habit_coaching")),
    AgentInfo("will", "Will", "LinkedIn and career: professional profile, job search, freelancing, networking, and resume support.", "planned", "eleven", ("linkedin", "jobs", "freelance", "resume")),
    AgentInfo("mike", "Mike", "Google Drive: find, organize, read, summarize, and manage files with connected and approved Drive access.", "planned", "eleven", ("drive", "files", "documents")),
    AgentInfo("dustin", "Dustin", "General day-to-day research, comparisons, fact-checking, learning, and evidence-based recommendations.", "active", "eleven", ("research", "compare", "fact_check")),
    AgentInfo("lucas", "Lucas", "Head of the Coding Department. Delegates engineering work to six equal-level coding specialists and coordinates their results.", "active", "eleven", ("software_development", "code_review", "coordination")),
    AgentInfo("frontend", "Frontend Agent", "Full-spectrum frontend engineering: HTML, CSS, JavaScript, TypeScript, web frameworks, UI systems, responsive UX, accessibility, APIs, tooling, performance, and frontend testing.", "active", "lucas", (
        "html", "html5", "css", "css3", "javascript", "es6_plus", "typescript",
        "bootstrap", "tailwind_css", "sass", "scss", "less",
        "react", "react_js", "nextjs", "angular", "vue", "nuxt", "svelte", "sveltekit", "astro", "jquery",
        "redux", "redux_toolkit", "zustand", "context_api", "tanstack_query",
        "material_ui", "mui", "ant_design", "chakra_ui", "shadcn_ui",
        "responsive_design", "mobile_first", "ui_ux", "figma_to_code",
        "accessibility", "wcag", "cross_browser", "animations",
        "rest_api", "graphql", "websocket", "authentication_integration",
        "vite", "webpack", "npm", "yarn", "pnpm", "git", "github",
        "eslint", "prettier", "jest", "vitest", "react_testing_library",
        "cypress", "playwright", "seo", "core_web_vitals",
        "performance_optimization", "lazy_loading", "code_splitting",
    )),
    AgentInfo("mobile", "Mobile Agent", "Full-spectrum mobile engineering across native, cross-platform, hybrid, device APIs, app architecture, UX, security, testing, and store delivery.", "active", "lucas", (
        "flutter", "dart", "react_native", "javascript_mobile", "typescript_mobile", "expo",
        "android", "kotlin", "java_android", "jetpack_compose",
        "ios", "swift", "swiftui", "uikit",
        "dotnet_maui", "xamarin", "ionic", "capacitor", "cordova",
        "kotlin_multiplatform", "native_script", "pwa",
        "mobile_ui_ux", "responsive_mobile_design", "navigation", "state_management",
        "rest_api", "graphql", "websocket", "authentication", "push_notifications",
        "camera", "gps", "maps", "bluetooth", "biometrics", "deep_links",
        "local_storage", "sqlite_mobile", "realm", "firebase", "offline_first",
        "mobile_security", "app_performance", "accessibility",
        "unit_testing", "widget_testing", "integration_testing", "appium", "detox",
        "fastlane", "play_store_release", "app_store_release", "ci_cd_mobile",
    )),
    AgentInfo("backend", "Backend Agent", "Full-spectrum server-side engineering across languages, frameworks, APIs, distributed systems, security, integrations, deployment, and operations.", "active", "lucas", (
        "java", "spring", "spring_boot", "jakarta_ee", "quarkus", "micronaut",
        "python", "django", "flask", "fastapi",
        "php", "laravel", "symfony", "composer",
        "csharp", "dotnet", "aspnet", "aspnet_core", "entity_framework",
        "nodejs", "express", "nestjs", "fastify",
        "go", "golang", "ruby", "rails", "rust", "c", "cpp", "c_plus_plus",
        "rest_api", "graphql", "grpc", "websocket", "webhooks",
        "authentication", "authorization", "oauth2", "openid_connect", "jwt",
        "api_security", "input_validation", "rate_limiting", "encryption",
        "microservices", "monoliths", "event_driven", "message_queues",
        "kafka", "rabbitmq", "redis", "caching",
        "docker", "kubernetes", "serverless", "cloud_deployment",
        "linux", "nginx", "apache", "ci_cd", "observability", "logging", "monitoring",
        "unit_testing", "integration_testing", "api_testing", "performance",
    )),
    AgentInfo("database", "Database Agent", "Full-spectrum data engineering across relational, document, key-value, wide-column, graph, and cloud databases, including architecture, reliability, security, and optimization.", "active", "lucas", (
        "sql", "postgresql", "postgres", "mysql", "mariadb", "sql_server",
        "oracle_database", "sqlite", "db2",
        "mongodb", "redis", "cassandra", "dynamodb", "firebase", "firestore",
        "cosmos_db", "couchbase", "couchdb", "elasticsearch", "opensearch",
        "neo4j", "influxdb", "clickhouse", "snowflake", "bigquery", "redshift",
        "relational_modeling", "document_modeling", "graph_modeling",
        "schema_design", "normalization", "denormalization", "indexing",
        "query_optimization", "execution_plans", "stored_procedures", "triggers",
        "transactions", "acid", "isolation_levels", "locking", "concurrency",
        "migrations", "orm", "hibernate", "sqlalchemy", "entity_framework",
        "backup", "restore", "replication", "sharding", "partitioning",
        "high_availability", "disaster_recovery", "data_integrity",
        "database_security", "encryption_at_rest", "access_control", "auditing",
        "etl", "elt", "data_warehousing", "data_modeling", "performance_monitoring",
    )),
    AgentInfo("testing", "Testing Agent", "Full-spectrum quality engineering across manual and automated testing, all application layers, reliability, security, performance, accessibility, and release quality.", "active", "lucas", (
        "manual_testing", "exploratory_testing", "test_planning", "test_cases",
        "unit_testing", "integration_testing", "system_testing", "end_to_end_testing",
        "regression_testing", "smoke_testing", "sanity_testing", "acceptance_testing",
        "api_testing", "ui_testing", "mobile_testing", "cross_browser_testing",
        "performance_testing", "load_testing", "stress_testing", "soak_testing",
        "security_testing", "accessibility_testing", "compatibility_testing",
        "selenium", "playwright", "cypress", "appium", "detox",
        "jest", "vitest", "pytest", "unittest", "junit", "testng",
        "postman", "newman", "rest_assured", "karate",
        "jmeter", "k6", "gatling", "locust", "owasp_zap", "burp_suite",
        "mocking", "contract_testing", "snapshot_testing", "visual_regression",
        "test_automation", "test_data_management", "defect_tracking",
        "root_cause_analysis", "coverage_analysis", "ci_cd_testing",
        "release_validation", "quality_reporting",
    )),
    AgentInfo("devops", "DevOps Agent", "Delivery and operations engineering: CI/CD, GitHub Actions, Docker, deployment architecture, infrastructure as code, release and rollback, monitoring, incident response, operational runbooks, and DevOps security. Production changes require explicit approval.", "active", "lucas", (
        "ci_cd", "github_actions", "workflow_automation", "build_pipelines",
        "test_automation", "artifact_management", "docker", "dockerfile",
        "docker_compose", "container_security", "container_registry",
        "linux", "bash", "powershell", "nginx", "apache", "reverse_proxy",
        "dns", "tls", "ssl", "https", "environment_configuration",
        "secrets_management", "least_privilege", "oidc", "terraform",
        "infrastructure_as_code", "ansible", "kubernetes", "helm",
        "cloud_deployment", "provider_independent_deployment", "release_management",
        "blue_green_deployment", "rolling_deployment", "rollback",
        "health_checks", "monitoring", "logging", "metrics", "tracing",
        "observability", "uptime", "incident_response", "runbooks",
        "dependency_scanning", "supply_chain_security", "workflow_security",
        "backup_strategy", "disaster_recovery",
    )),
)

 
def list_agents() -> list[dict[str, object]]:
    return [
        {
            "name": agent.name,
            "title": agent.title,
            "description": agent.description,
            "status": agent.status,
            "parent": agent.parent,
            "capabilities": list(agent.capabilities),
        }
        for agent in AGENTS
    ]


def route_agent(message: str) -> str:
    """Choose the best top-level department for a user request."""
    text = " ".join(message.lower().split())

    routes = (
        ("max", ("workout", "fitness", "diet", "nutrition", "food log", "food diary", "meal plan",
                 "calorie", "calories", "macros", "protein", "carbs", "fat loss", "weight loss",
                 "weight gain", "weight trend", "weekly weight", "weight tracking", "body measurement", "body measurements", "muscle", "gym",
                 "body fat", "exercise", "steps", "hydration", "recovery", "वजन", "डाइट",
                 "वर्कआउट", "खाना", "कैलोरी", "प्रोटीन", "मसल")),
        ("will", ("linkedin", "job opening", "job openings", "job search", "freelance",
                  "freelancing", "resume", "cv", "career", "नौकरी", "रिज्यूमे")),
        ("mike", ("google drive", "drive file", "drive folder", "my documents", "file in drive",
                  "गूगल ड्राइव")),
        ("lucas", ("debug", "bug", "stack trace", "exception", "python", "django", "flask", "fastapi",
                   "javascript", "typescript", "html", "css", "sass", "scss", "less", "bootstrap",
                   "tailwind", "react", "next.js", "nextjs", "angular", "vue", "nuxt", "svelte",
                   "astro", "redux", "zustand", "playwright", "cypress", "selenium", "jest", "vitest",
                   "flutter", "dart", "react native", "android", "kotlin", "swift", "swiftui",
                   "ionic", "xamarin", ".net maui", "java", "spring", "php", "laravel", "asp.net",
                   "c#", "c++", "rust", "ruby", "golang", "node.js", "nestjs", "express",
                   "devops", "ci/cd", "ci cd", "github actions", "docker", "dockerfile",
                   "docker compose", "deploy", "deployment", "terraform", "kubernetes",
                   "nginx", "monitoring", "observability", "pipeline", "hostinger",
                   "sql", "database", "mongodb", "postgres", "mysql", "redis", "cassandra",
                   "dynamodb", "api", "code", "coding", "program", "function", "github repo",
                   "ऐप बनाओ", "कोड")),
        ("dustin", ("research", "investigate", "compare", "comparison", "sources",
                    "latest information", "market analysis", "competitor", "fact check",
                    "अध्ययन", "तुलना", "रिसर्च")),
    )
    for agent_name, phrases in routes:
        if any(phrase in text for phrase in phrases):
            return agent_name
    return "eleven"


AGENT_INSTRUCTIONS = {
    "eleven": (
        "You are Eleven (11), also called L, the overall assistant and central coordinator. "
        "Understand the goal, choose the correct department, coordinate multiple departments "
        "when needed, and report one clear result. Never claim a specialist or external tool "
        "performed work unless execution was actually confirmed."
    ),
    "max": (
        "You are Max, Eleven’s personal health and fitness specialist. Manage daily food and drink logs, estimate calories and macros with clearly stated uncertainty, compare intake with the user’s goals, suggest practical meals and substitutions, plan and review workouts, track activity and recovery, interpret weight trends and body measurements, and give realistic progress projections as ranges rather than promises. Ask for missing quantities, cooked/raw state, brands, preparation methods, workout sets/reps, and weigh-in conditions when these materially affect an estimate. Prefer weekly weight averages over single-day fluctuations. Never shame the user, prescribe crash diets, encourage extreme deficits, diagnose conditions, or change medication. Flag symptoms, eating-disorder signals, unsafe restriction, or medical concerns and recommend a qualified clinician or registered dietitian. Do not infer that a food or workout was completed unless the user logged it. Treat logged health data as private, use only the owner’s records, and distinguish estimates from measured facts."
    ),
    "will": (
        "You are Will, responsible for LinkedIn and career support: profile improvement, jobs, "
        "freelancing, networking, and resumes. Do not claim LinkedIn access or take profile "
        "actions, send messages, or apply unless a connected tool confirms it and approval exists."
    ),
    "mike": (
        "You are Mike, responsible for Google Drive files and documents. Help find, organize, "
        "read, and summarize files when Drive access is connected. Never claim access or modify, "
        "share, or delete files without the required tool and user approval."
    ),
    "dustin": (
        "You are Dustin, the general research specialist for day-to-day questions. For current "
        "or consequential claims, use reliable sources when available, distinguish verified "
        "facts from inference, and state uncertainty."
    ),
    "lucas": (
        "You are Lucas, head of the Coding Department. You coordinate six equal-level, "
        "domain-complete specialists: Frontend (full-spectrum web), Mobile (native, cross-platform "
        "and hybrid mobile), Backend (server-side languages and systems), Database (relational, "
        "NoSQL, analytics and data infrastructure), and Testing (manual, automation, performance, "
        "security and release QA), and DevOps (CI/CD, containers, infrastructure, deployment, observability, incident response and delivery security). Match tasks to the right specialist or combination, coordinate "
        "interfaces and dependencies, integrate results, require independent verification, and "
        "report exactly what was and was not executed. A listed capability is knowledge scope, not "
        "proof a tool/runtime is installed or connected. Do not claim repository changes unless a "
        "connected GitHub tool confirms them."
    ),
}
