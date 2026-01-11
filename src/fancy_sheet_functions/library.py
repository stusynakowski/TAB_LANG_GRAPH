from typing import Callable, List, Type
import functools
import scrapetube
import logging
from .registry import WorkflowRegistry

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fancy_sheet_functions.library")

# Decorator to mark functions for auto-registration
_EXPOSED_FUNCTIONS = []

def exposed(name: str = None, description: str = "", complexity: str = "quick"):
    """
    complexity: 'quick' for instant calculations, 'heavy' for network/IO bound tasks.
    """
    def decorator(func: Callable):
        _EXPOSED_FUNCTIONS.append({
            "func": func,
            "name": name or func.__name__,
            "description": description or func.__doc__ or "",
            "complexity": complexity
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
            description=item["description"],
            metadata={"complexity": item["complexity"]}
        )

# --- Define your functions below ---

@exposed(name="ToUpper", description="Converts a string to uppercase", complexity="quick")
def to_upper(text: str) -> str:
    return text.upper()

@exposed(name="ToLower", description="Converts a string to lowercase", complexity="quick")
def to_lower(text: str) -> str:
    return text.lower()

@exposed(name="Concatenate", description="Joins two strings", complexity="quick")
def concatenate(a: str, b: str) -> str:
    return f"{a}{b}"

@exposed(name="Sum", description="Adds two numbers", complexity="quick")
def sum_numbers(a: float, b: float) -> float:
    return a + b

@exposed(name="LLM_SUMARIZE_TEST", description="[Mock] Summarizes text using an LLM", complexity="heavy")
def mock_summarize(text: str) -> str:
    # This is a placeholder for a real LLM call
    return f"Summary of '{text[:20]}...': This is a distinct summary."

@exposed(name="GetYoutubeChannelVideos", description="Lists video URLs from a YouTube channel", complexity="heavy")
def get_youtube_channel_videos(channel_url: str, limit: int = 10) -> List[str]:
    """
    Fetches video URLs from a given YouTube channel URL.
    limit: The maximum number of videos to retrieve (default 10).
    """
    try:
        logger.info(f"Starting fetch for channel: {channel_url} (Limit: {limit})")
        # scrapetube returns a generator
        videos = scrapetube.get_channel(channel_url=channel_url)
        results = []
        
        # Enforce the limit to prevent timeouts/infinite loops
        for i, video in enumerate(videos):
            if i >= limit:
                logger.info("Limit reached.")
                break
            
            video_url = f"https://www.youtube.com/watch?v={video['videoId']}"
            results.append(video_url)
            
            # Log progress every video (or every N videos)
            logger.info(f"[{i+1}/{limit}] Found: {video['videoId']}")
            
        logger.info(f"Completed. Found {len(results)} videos.")
        return results
    except Exception as e:
        error_msg = f"Error fetching videos: {str(e)}"
        logger.error(error_msg)
        return [error_msg]
