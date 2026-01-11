from typing import Callable, List, Type
import functools
from .registry import WorkflowRegistry

# Decorator to mark functions for auto-registration
_EXPOSED_FUNCTIONS = []

def exposed(name: str = None, description: str = ""):
    def decorator(func: Callable):
        _EXPOSED_FUNCTIONS.append({
            "func": func,
            "name": name or func.__name__,
            "description": description or func.__doc__ or ""
        })
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator

def setup_library(registry: WorkflowRegistry):
    """
    Registers all exposed functions with the provided registry.
    """
    for item in _EXPOSED_FUNCTIONS:
        registry.register_function(
            name=item["name"],
            func=item["func"],
            description=item["description"]
        )

# --- Define your functions below ---

@exposed(name="ToUpper", description="Converts a string to uppercase")
def to_upper(text: str) -> str:
    return text.upper()

@exposed(name="ToLower", description="Converts a string to lowercase")
def to_lower(text: str) -> str:
    return text.lower()

@exposed(name="Concatenate", description="Joins two strings")
def concatenate(a: str, b: str) -> str:
    return f"{a}{b}"

@exposed(name="Sum", description="Adds two numbers")
def sum_numbers(a: float, b: float) -> float:
    return a + b

@exposed(name="LLM_SUMARIZE_TEST", description="[Mock] Summarizes text using an LLM")
def mock_summarize(text: str) -> str:
    # This is a placeholder for a real LLM call
    return f"Summary of '{text[:20]}...': This is a distinct summary."
