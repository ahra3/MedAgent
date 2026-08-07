from pathlib import Path

"""Versioned prompt loader — treats prompts as configuration, not code.

Prompts are stored as plain text files under src/config/prompts/<version>/.
This loader reads them by agent name and version, with fallback to latest.

Usage:
    from src.config.prompt_loader import load_prompt

    system_prompt = load_prompt("intake_agent")           # loads from latest version
    system_prompt = load_prompt("intake_agent", version="v1")  # loads specific version
"""



# Base directory for all prompt versions
PROMPTS_DIR = Path(__file__).parent / "prompts"


def get_latest_version() -> str:
    """Find the latest prompt version by sorting version directories.

    Returns:
        The name of the latest version directory (e.g., 'v1', 'v2').

    Raises:
        FileNotFoundError: If no version directories exist.
    """
    versions = sorted(
        [d.name for d in PROMPTS_DIR.iterdir() if d.is_dir() and d.name.startswith("v")],
    )
    if not versions:
        raise FileNotFoundError(f"No prompt versions found in {PROMPTS_DIR}")
    return versions[-1]


def load_prompt(agent_name: str, version: str | None = None) -> str:
    """Load a prompt template for a given agent and version.

    Args:
        agent_name: Name of the agent (matches the filename without extension).
                    e.g., 'intake_agent', 'ddi_agent', 'guidelines_rag_agent', 'synthesis_agent'
        version: Prompt version to load (e.g., 'v1'). If None, loads the latest version.

    Returns:
        The prompt text content as a string.

    Raises:
        FileNotFoundError: If the prompt file does not exist.
    """
    if version is None:
        version = get_latest_version()

    prompt_path = PROMPTS_DIR / version / f"{agent_name}.txt"

    if not prompt_path.exists():
        raise FileNotFoundError(
            f"Prompt not found: {prompt_path}. "
            f"Available prompts in {version}: "
            f"{[f.stem for f in (PROMPTS_DIR / version).glob('*.txt')]}"
        )

    return prompt_path.read_text(encoding="utf-8").strip()
