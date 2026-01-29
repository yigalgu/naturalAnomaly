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
        system_prompt = """You are an AI assistant specialized in traffic and vehicle analysis. 
You help users understand video analysis results by answering questions in a clear, concise manner.

Guidelines:
- Answer in Hebrew (עברית) when the question is in Hebrew
- Be specific and use numbers from the data
- Explain trends and patterns when relevant
- If asked about anomalies, look for unusual patterns in the data
- Keep answers concise but informative
"""
        
        # Prepare messages
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": f"{context_message}\n\nQuestion: {question}"
            }
        ]
        
        try:
            # Call Ollama
            response = chat(
                model=self.model,
                messages=messages
            )
            
            answer = response['message']['content']
            return answer
            
        except Exception as e:
            return f"מצטער, אירעה שגיאה בעיבוד השאלה: {str(e)}"
    
    def _build_context(self, context: Dict, video_filename: Optional[str] = None) -> str:
        """Build context message from video analysis data"""
        
        if not context:
            return "No video analysis data available yet. Please upload and process a video first."
        
        context_parts = ["Video Analysis Data:"]
        
        if video_filename:
            context_parts.append(f"- Video file: {video_filename}")
        
        if "total_vehicles" in context:
            context_parts.append(f"- Total vehicles detected: {context['total_vehicles']}")
        
        if "vehicles_per_hour" in context:
            context_parts.append(f"- Vehicles per hour: {context['vehicles_per_hour']}")
        
        if "vehicle_types" in context:
            types_str = ", ".join([f"{k}: {v}" for k, v in context['vehicle_types'].items()])
            context_parts.append(f"- Vehicle types: {types_str}")
        
        if "busiest_segment" in context and context["busiest_segment"]:
            seg = context["busiest_segment"]
            context_parts.append(
                f"- Busiest segment: Segment {seg.get('segment_number', 'N/A')} "
                f"(from {seg.get('start_time', 0):.1f}s to {seg.get('end_time', 0):.1f}s) "
                f"with {seg.get('vehicle_count', 0)} detections"
            )
        
        if "duration" in context:
            context_parts.append(f"- Video duration: {context['duration']:.1f} seconds")
        
        return "\n".join(context_parts)
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
