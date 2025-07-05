
"""
Literature Review Service - Bridge between AutoGen backend and Streamlit frontend
"""

import asyncio
import os
from datetime import datetime
from typing import Optional, Callable, List, Dict, Any
from dataclasses import dataclass
from enum import Enum
import time
import re

# Import your AutoGen backend
from agent_backend import create_literature_review_team


class ReviewStatus(Enum):
    """Status of the literature review process"""
    INITIALIZING = "initializing"
    SEARCHING = "searching"
    SUMMARIZING = "summarizing"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class ReviewProgress:
    """Progress information for the literature review"""
    status: ReviewStatus
    message: str
    progress_percent: float
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class ReviewConfig:
    """Configuration for literature review"""
    topic: str
    max_results: int = 5
    model_name: str = "deepseek/deepseek-chat"
    max_turns: int = 2
    api_key: str = None


@dataclass
class ReviewResult:
    """Result of the literature review"""
    success: bool
    content: str = ""
    error_message: str = ""
    execution_time: float = 0.0
    config: ReviewConfig = None
    papers_found: int = 0


class LiteratureReviewService:
    """Service for running literature reviews with progress tracking"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAIROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required")
    
    def is_function_call_message(self, content: str) -> bool:
        """Check if the message content is a function call or function result"""
        if not content or not isinstance(content, str):
            return False
        
        # Check for function call patterns
        function_indicators = [
            '[FunctionCall(',
            '[FunctionExecutionResult(',
            'call_id=',
            'arguments=',
            'name=\'arxive_search\'',
            'name="arxive_search"',
            '"query":',
            '"max_result":',
            'pdf_url',
            'published',
            'authors'
        ]
        
        return any(indicator in content for indicator in function_indicators)
    
    def is_raw_json_data(self, content: str) -> bool:
        """Check if content is raw JSON data from function results"""
        if not content or not isinstance(content, str):
            return False
        
        # Check for JSON structure with paper data
        json_indicators = [
            "'title':",
            "'authors':",
            "'published':",
            "'summary':",
            "'pdf_url':",
            "{'title':",
            '{"title":'
        ]
        
        return any(indicator in content for indicator in json_indicators)
    
    def extract_final_review_only(self, content: str) -> str:
        """Extract only the final formatted literature review"""
        if not content:
            return ""
        
        # Look for the final literature review section
        # It usually starts with "Literature Review:" or similar
        lines = content.split('\n')
        review_started = False
        review_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines at the beginning
            if not review_started and not line:
                continue
                
            # Check if this line starts the actual review
            if not review_started and ('Literature Review:' in line or 
                                     'Key Papers' in line or
                                     (line and not self.is_function_call_message(line) and 
                                      not self.is_raw_json_data(line))):
                review_started = True
                review_lines.append(line)
            elif review_started:
                review_lines.append(line)
        
        return '\n'.join(review_lines).strip()
    
    def clean_content(self, content: str) -> str:
        """Clean and filter content to remove function calls and duplicates"""
        if not content:
            return ""
        
        # Split into sections
        sections = content.split('\n\n')
        clean_sections = []
        seen_content = set()
        
        for section in sections:
            section = section.strip()
            
            # Skip empty sections
            if not section:
                continue
            
            # Skip function calls and raw data
            if self.is_function_call_message(section) or self.is_raw_json_data(section):
                continue
            
            # Skip duplicates (simple deduplication)
            if section in seen_content:
                continue
            
            seen_content.add(section)
            clean_sections.append(section)
        
        # Join sections and extract final review
        cleaned_content = '\n\n'.join(clean_sections)
        final_review = self.extract_final_review_only(cleaned_content)
        
        return final_review if final_review else cleaned_content
    
    def extract_message_content(self, msg) -> str:
        """Extract content from different message types safely"""
        try:
            # Check for common attributes in order of preference
            if hasattr(msg, 'content') and msg.content:
                return str(msg.content)
            elif hasattr(msg, 'summary') and msg.summary:
                return str(msg.summary)
            elif hasattr(msg, 'messages') and msg.messages:
                # If it's a container with messages, extract from the last message
                last_msg = msg.messages[-1] if isinstance(msg.messages, list) else msg.messages
                return self.extract_message_content(last_msg)
            elif hasattr(msg, 'inner_messages') and msg.inner_messages:
                # Another possible container attribute
                last_msg = msg.inner_messages[-1] if isinstance(msg.inner_messages, list) else msg.inner_messages
                return self.extract_message_content(last_msg)
            elif hasattr(msg, 'text') and msg.text:
                return str(msg.text)
            elif hasattr(msg, 'message') and msg.message:
                return str(msg.message)
            else:
                # If we can't find content, return empty string
                return ""
        except Exception as e:
            return ""
    
    async def run_review(
        self, 
        config: ReviewConfig, 
        progress_callback: Optional[Callable[[ReviewProgress], None]] = None
    ) -> ReviewResult:
        """
        Run a literature review with progress tracking
        
        Args:
            config: Review configuration
            progress_callback: Optional callback for progress updates
            
        Returns:
            ReviewResult with success status and content
        """
        start_time = time.time()
        
        def update_progress(status: ReviewStatus, message: str, percent: float):
            if progress_callback:
                progress_callback(ReviewProgress(status, message, percent))
        
        try:
            # Initialize
            update_progress(ReviewStatus.INITIALIZING, "Initializing agents...", 10)
            
            # Create the team
            team = create_literature_review_team(
                model_name=config.model_name,
                api_key=self.api_key
            )
            
            # Start search
            update_progress(ReviewStatus.SEARCHING, f"Searching for papers on '{config.topic}'...", 25)
            
            # Create the task
            task = f"conduct a literature review on the topic - {config.topic} and return exactly {config.max_results} papers"
            
            # Collect results
            all_messages = []
            message_count = 0
            
            update_progress(ReviewStatus.SUMMARIZING, "Analyzing papers and generating review...", 50)
            
            # Run the team and collect messages
            async for msg in team.run_stream(task=task):
                message_count += 1
                
                # Extract content safely
                content = self.extract_message_content(msg)
                if content:  # Only add non-empty content
                    all_messages.append(content)
                
                # Update progress based on message count
                if message_count == 1:
                    update_progress(ReviewStatus.SEARCHING, "Papers found, starting analysis...", 60)
                elif message_count >= 2:
                    update_progress(ReviewStatus.SUMMARIZING, "Generating final review...", 80)
            
            # Combine all messages and clean
            raw_content = '\n\n'.join(all_messages)
            cleaned_content = self.clean_content(raw_content)
            
            # Complete
            execution_time = time.time() - start_time
            update_progress(ReviewStatus.COMPLETED, "Literature review completed successfully!", 100)
            
            return ReviewResult(
                success=True,
                content=cleaned_content,
                execution_time=execution_time,
                config=config,
                papers_found=config.max_results
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Error during literature review: {str(e)}"
            update_progress(ReviewStatus.ERROR, error_msg, 0)
            
            return ReviewResult(
                success=False,
                error_message=error_msg,
                execution_time=execution_time,
                config=config
            )


def create_literature_review_service(api_key: str = None) -> LiteratureReviewService:
    """Factory function to create a literature review service"""
    return LiteratureReviewService(api_key=api_key)



def debug_message_structure(msg):
    """Debug function to understand message structure"""
    print(f"Message type: {type(msg)}")
    print(f"Available attributes: {[attr for attr in dir(msg) if not attr.startswith('_')]}")
    if hasattr(msg, '__dict__'):
        print(f"Message dict: {msg.__dict__}")
    print("-" * 30)