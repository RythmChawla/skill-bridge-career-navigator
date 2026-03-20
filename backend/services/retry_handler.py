"""Retry handler with exponential backoff for API calls"""
import logging
import time
from typing import Callable, TypeVar, Any
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


def retry_with_backoff(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 10.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for retrying function calls with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplication factor for delay between retries
        max_delay: Maximum delay cap in seconds
        exceptions: Tuple of exceptions to catch and retry on
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            attempt = 0
            delay = initial_delay
            
            while attempt < max_attempts:
                try:
                    logger.debug(f"Attempt {attempt + 1}/{max_attempts} for {func.__name__}")
                    return func(*args, **kwargs)
                    
                except exceptions as e:
                    attempt += 1
                    
                    if attempt >= max_attempts:
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}")
                        raise
                    
                    # Calculate delay with backoff
                    delay = min(initial_delay * (backoff_factor ** (attempt - 1)), max_delay)
                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt}/{max_attempts}): {str(e)}. "
                        f"Retrying in {delay:.1f}s..."
                    )
                    time.sleep(delay)
            
        return wrapper
    return decorator


class APIRetryManager:
    """Manages retries for different types of API errors"""
    
    @staticmethod
    def handle_gemini_error(error: Exception, attempt: int = 1) -> tuple[bool, float]:
        """
        Determine if an error is retryable and calculate delay.
        
        Returns:
            (is_retryable, delay_seconds)
        """
        error_msg = str(error)
        
        # Rate limiting (429) - retryable with longer delay
        if "429" in error_msg or "quota" in error_msg.lower():
            delay = min(10 * (2 ** (attempt - 1)), 300)  # Max 5 minutes
            return True, delay
        
        # Timeout - retryable
        if "timeout" in error_msg.lower() or "deadline" in error_msg.lower():
            delay = 2 * (2 ** (attempt - 1))
            return True, delay
        
        # Service unavailable (503) - retryable
        if "503" in error_msg or "unavailable" in error_msg.lower():
            delay = 5 * (2 ** (attempt - 1))
            return True, delay
        
        # Invalid API key, malformed request - not retryable
        if any(x in error_msg for x in ["401", "403", "invalid", "api_key", "authenticate"]):
            return False, 0
        
        # Default: retryable once
        return True, 2
    
    @staticmethod
    def get_fallback_value(data_type: str, context: dict = None) -> Any:
        """Get appropriate fallback value when API fails"""
        fallbacks = {
            "feedback": "We're having trouble generating personalized feedback right now. "
                       "Based on your skills, focus on learning the missing skills in priority order!",
            "roadmap": [
                {
                    "step": 1,
                    "title": "Foundation Building",
                    "description": "Start with the fundamentals of your target skills",
                    "timeframe": "2-3 weeks",
                    "what": "Core concepts and basics",
                    "how": "Online courses and tutorials",
                    "practice": "Simple practice problems"
                },
                {
                    "step": 2,
                    "title": "Intermediate Practice",
                    "description": "Build small projects to reinforce learning",
                    "timeframe": "3-4 weeks",
                    "what": "Applied skills and techniques",
                    "how": "Build real-world mini projects",
                    "practice": "Personal projects and exercises"
                },
                {
                    "step": 3,
                    "title": "Advanced Application",
                    "description": "Apply skills to complex, real-world scenarios",
                    "timeframe": "4-6 weeks",
                    "what": "Advanced patterns and optimization",
                    "how": "Contribute to open source or build portfolio",
                    "practice": "Production-quality projects"
                }
            ],
            "resume_extraction": {
                "personal_info": {"name": "", "location": ""},
                "contact": {"email": "", "phone": "", "linkedin": "", "github": "", "portfolio": ""},
                "skills": [],
                "education": [],
                "experience": [],
                "projects": [],
                "extraction_status": "partial"  # Indicates fallback was used
            }
        }
        return fallbacks.get(data_type, {})
