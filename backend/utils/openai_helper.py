from openai import OpenAI
import os


class OpenAIHelper:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        api_base = os.getenv('OPENAI_API_BASE')
        
        # Initialize OpenAI client with custom base URL if provided
        if api_base:
            self.client = OpenAI(api_key=api_key, base_url=api_base)
        else:
            self.client = OpenAI(api_key=api_key)
        
        # Use gpt-4o-mini for better compatibility with custom API endpoints
        self.model = "gpt-4o-mini"
        self.temperature = 0.7
        
        self.system_prompt = """You are a web scraping assistant. You analyze website content and extract only the information the user requests. 

Your responses should be:
- Clear and human-readable (no JSON, XML, or raw data)
- Focused on the specific information requested
- Well-organized with proper formatting
- Concise but complete

If the user asks for specific data points (like prices, names, dates), present them in a clean, readable format."""
    
    def generate_response(self, user_prompt: str, website_content: str = None, 
                         conversation_history: list = None) -> dict:
        """
        Generate AI response based on user prompt and context
        
        Args:
            user_prompt: User's question or request
            website_content: Scraped website content (optional)
            conversation_history: Previous messages for context (optional)
            
        Returns:
            {
                'success': bool,
                'response': str,
                'error': str|None
            }
        """
        try:
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add conversation history
            if conversation_history:
                messages.extend(conversation_history)
            
            # Build user message
            user_message = user_prompt
            if website_content:
                user_message = f"Website Content:\n\n{website_content}\n\nUser Request: {user_prompt}"
            
            messages.append({"role": "user", "content": user_message})
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=2000
            )
            
            return {
                'success': True,
                'response': response.choices[0].message.content,
                'error': None
            }
            
        except Exception as e:
            # Log the full error for debugging
            print(f"OpenAI API Error: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return {
                'success': False,
                'response': '',
                'error': str(e)
            }
