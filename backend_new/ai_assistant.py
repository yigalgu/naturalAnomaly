from ollama import chat
from typing import Dict, Optional

class AIAssistant:
    """AI assistant for answering questions about video analysis"""
    
    def __init__(self, model: str = "llama3.2"):
        self.model = model
        self.conversation_history = []
    
    def ask(self, question: str, context: Dict, video_filename: Optional[str] = None) -> str:
        """
        Ask a question about the video analysis
        
        Args:
            question: User's question
            context: Video analysis data (statistics, detections, etc.)
            video_filename: Name of the video file
            
        Returns:
            AI-generated answer
        """
        # Build context message
        context_message = self._build_context(context, video_filename)
        
        # Create system prompt
        system_prompt = """You are a friendly traffic analysis expert helping users understand their video footage.

🎯 YOUR PERSONALITY:
- Speak naturally like a knowledgeable friend, not a robot
- Be enthusiastic about interesting findings
- Use casual language while staying professional
- Show curiosity and engagement with the user's questions

📝 RESPONSE STYLE:
- Keep answers SHORT (1-3 sentences unless asked for details)
- Answer the question DIRECTLY first, then add context if needed
- Use numbers and specifics from the data
- Avoid technical jargon - say "vehicles" not "detected objects"
- NO phrases like "based on the analysis" or "the data shows" - just answer naturally
- Use emojis sparingly (🚗 🚌 🏍️ 🚛) only when it adds clarity

🌍 LANGUAGE:
- Respond in the SAME language as the question
- Hebrew: casual, friendly Hebrew (like texting a friend)
- English: natural, conversational English

⚠️ ANOMALIES:
- If asked about unusual things, look for:
  * Vehicles stopping in odd places
  * Unusually high/low traffic
  * Sudden changes in traffic patterns
  * Anything that stands out from the norm

💬 EXAMPLES OF GOOD RESPONSES:

User: "What's in this video?"
Bot: "This is a city intersection with moderate traffic. I spotted 45 vehicles over 90 seconds - mostly cars with a few trucks mixed in."

User: "מה קורה בסרטון?"
Bot: "זה צומת עירוני עם תנועה בינונית. זיהיתי 45 כלי רכב ב-90 שניות - בעיקר מכוניות עם כמה משאיות."

User: "Any anomalies?"
Bot: "Yeah, there's one thing - at second 47, a white car stops in the middle of the lane for about 8 seconds. Everything else looks normal."

User: "כמה משאיות?"
Bot: "7 משאיות, בערך 15% מהתנועה."

User: "ומה עם אוטובוסים?"
Bot: "רק 2 אוטובוסים - אחד בשנייה 30 ואחד ב-75."

Remember: Be helpful, natural, and conversational. You're having a chat, not writing a report!
"""
        
        # Prepare messages with conversation history
        messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]
        
        # Add conversation history
        messages.extend(self.conversation_history)
        
        # Add current question
        # Only include full context on first message, otherwise just the question
        if len(self.conversation_history) == 0:
            # First message - include full context
            current_message = {
                "role": "user",
                "content": f"Here's the video data:\n{context_message}\n\nQuestion: {question}"
            }
        else:
            # Subsequent messages - just the question
            current_message = {
                "role": "user",
                "content": question
            }
        messages.append(current_message)
        
        try:
            # Call Ollama
            response = chat(
                model=self.model,
                messages=messages
            )
            
            answer = response['message']['content']
            
            # Save to conversation history
            self.conversation_history.append(current_message)
            self.conversation_history.append({
                "role": "assistant",
                "content": answer
            })
            
            # Keep only last 10 messages (5 exchanges) to avoid token limits
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            return answer
            
        except Exception as e:
            return f"מצטער, אירעה שגיאה בעיבוד השאלה: {str(e)}"
    
    def _build_context(self, context: Dict, video_filename: Optional[str] = None) -> str:
        """Build context message from video analysis data"""
        
        if not context:
            return "No video analysis data available yet. Please upload and process a video first."
        
        # Build a clean, natural context
        parts = []
        
        if video_filename:
            parts.append(f"Video: {video_filename}")
        
        if "duration" in context:
            parts.append(f"Duration: {context['duration']:.1f} seconds")
        
        if "total_vehicles" in context:
            parts.append(f"Total vehicles: {context['total_vehicles']}")
        
        if "vehicles_per_hour" in context:
            parts.append(f"Rate: {context['vehicles_per_hour']} vehicles/hour")
        
        if "vehicle_types" in context and context["vehicle_types"]:
            types_list = [f"{count} {vtype}" for vtype, count in context['vehicle_types'].items()]
            parts.append(f"Types: {', '.join(types_list)}")
        
        if "busiest_segment" in context and context["busiest_segment"]:
            seg = context["busiest_segment"]
            start = seg.get('start_time', 0)
            end = seg.get('end_time', 0)
            count = seg.get('vehicle_count', 0)
            parts.append(f"Busiest period: {start:.1f}s-{end:.1f}s ({count} detections)")
        
        return "\n".join(parts)
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
