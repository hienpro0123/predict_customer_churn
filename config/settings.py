import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


def _get_bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def load_local_env_file() -> None:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key and key not in os.environ:
            os.environ[key] = value


if load_dotenv:
    load_dotenv()
else:
    load_local_env_file()


DATABRICKS_URL = os.getenv("DATABRICKS_URL", "").strip()
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN", "").strip()
API_TIMEOUT_SECONDS = int(os.getenv("DATABRICKS_TIMEOUT", "30"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
GEMINI_TIMEOUT_SECONDS = int(os.getenv("GEMINI_TIMEOUT", "30"))
DISABLE_OUTBOUND_PROXY = _get_bool_env("DISABLE_OUTBOUND_PROXY", default=False)

FEATURE_COLUMNS = [
    "Age",
    "Gender",
    "Tenure",
    "Usage Frequency",
    "Support Calls",
    "Payment Delay",
    "Subscription Type",
    "Contract Length",
    "Total Spend",
    "Last Interaction",
    "Age_group",
    "Usage_Per_Tenure",
    "Spend_Per_Usage",
    "Spend_Per_Tenure",
    "Payment_Delay_Ratio",
    "Engagement_Score",
]

CONTRACT_LENGTH_MAPPING = {
    "Monthly": "1 month",
    "Quarterly": "3 months",
    "Annual": "12 months",
}

REQUEST_HEADERS = {
    "Content-Type": "application/json",
}
