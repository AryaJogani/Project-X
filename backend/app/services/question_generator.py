"""
LLM-powered progressive question generation
"""

from typing import List, Dict, Optional, AsyncGenerator
import json
import logging
from datetime import datetime

from app.models.gap import Gap
from app.models.question import Question

logger = logging.getLogger(__name__)

class QuestionGeneratorService:
    """
    LLM-powered progressive question generation with RAG integration
    """
    
    def __init__(self, llm_orchestrator, vector_service=None):
        self.llm = llm_orchestrator
        self.vector_service = vector_service
    
    async def generate_questions(
        self,
        gap: Gap,
        context: Optional[Dict] = None
    ) -> List[Question]:
        """
        Generate progressive questions for a gap
        
        Args:
            gap: The knowledge gap to address
            context: Additional context for generation
            
        Returns:
            List of progressive questions
        """
        
        logger.info(f"Generating questions for gap: {gap.id}")
        
        # Build context-enhanced prompt
        prompt = await self._build_question_prompt(gap, context)
        
        # Generate questions using LLM
        response = await self.llm.generate(
            task_type="question_generation",
            prompt=prompt,
            context={"gap": gap.__dict__},
            max_tokens=2000,
            temperature=0.7  # Higher temp for creative questions
        )
        
        # Parse response
        try:
            questions_data = json.loads(response["content"])
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse question generation response: {e}")
            return []
        
        # Create Question objects
        questions = []
        for level_idx, q_data in enumerate(questions_data.get("questions", []), 1):
            question = Question(
                gap_id=gap.id,
                level=level_idx,
                content=q_data.get("question", ""),
                context=q_data.get("context", ""),
                answer_type=q_data.get("answer_type", "text"),
                depends_on=q_data.get("depends_on"),
                generated_by="llm_orchestrator",
                generation_context={
                    "gap_type": gap.type,
                    "gap_severity": gap.severity,
                    "generation_timestamp": datetime.now().isoformat()
                }
            )
            questions.append(question)
        
        logger.info(f"Generated {len(questions)} questions for gap: {gap.id}")
        return questions
    
    async def _build_question_prompt(
        self,
        gap: Gap,
        context: Optional[Dict]
    ) -> str:
        """
        Build context-aware question generation prompt
        """
        
        # Get similar content from vector store if available
        similar_context = ""
        if self.vector_service:
            try:
                similar_docs = await self.vector_service.search(
                    query=f"{gap.description} {gap.location}",
                    n_results=3
                )
                if similar_docs and similar_docs.get("documents"):
                    similar_context = "\n\n".join([
                        f"Similar Section:\n{doc}"
                        for doc in similar_docs["documents"][0]
                    ])
            except Exception as e:
                logger.warning(f"Vector search failed: {e}")
        
        return f"""
You are an ESG (Environmental, Social, Governance) knowledge expert.
Generate progressive disclosure questions to fill this knowledge gap.

Gap Information:
- Type: {gap.type}
- Severity: {gap.severity}
- Location: {gap.location}
- Description: {gap.description}

Document Context:
{context.get('document_excerpt', 'N/A') if context else 'N/A'}

Similar Content from Knowledge Base:
{similar_context}

Generate exactly 4 questions following progressive disclosure:

Level 1 (Overview): Broad, high-level question about what/why
Level 2 (Context): Questions about when/where/who/scope
Level 3 (Depth): Detailed questions about how/process/methodology
Level 4 (Validation): Questions for examples/evidence/metrics

Requirements:
- Questions must be clear and specific
- Each level builds on previous answers
- Include context for why each question matters
- Specify expected answer type (text, number, date, list, table)
- Make questions relevant to ESG reporting standards
- Consider the gap severity in question complexity

Return JSON format:
{{
  "questions": [
    {{
      "level": 1,
      "question": "...",
      "context": "...",
      "answer_type": "text|number|date|list|table",
      "depends_on": null
    }},
    {{
      "level": 2,
      "question": "...",
      "context": "...",
      "answer_type": "text|number|date|list|table",
      "depends_on": 1
    }},
    {{
      "level": 3,
      "question": "...",
      "context": "...",
      "answer_type": "text|number|date|list|table",
      "depends_on": 2
    }},
    {{
      "level": 4,
      "question": "...",
      "context": "...",
      "answer_type": "text|number|date|list|table",
      "depends_on": 3
    }}
  ]
}}
"""
    
    async def refine_question(
        self,
        question: Question,
        user_feedback: str
    ) -> Question:
        """
        Refine a question based on user feedback
        """
        
        prompt = f"""
Original question: {question.content}
Question context: {question.context}
User feedback: {user_feedback}

Improve the question based on this feedback while maintaining its purpose.
Keep it clear, specific, and relevant to ESG reporting.

Return improved question as JSON: {{"question": "...", "context": "..."}}
"""
        
        try:
            response = await self.llm.generate(
                task_type="question_generation",
                prompt=prompt,
                max_tokens=500,
                temperature=0.7
            )
            
            improved = json.loads(response["content"])
            question.content = improved["question"]
            question.context = improved["context"]
            
            return question
            
        except Exception as e:
            logger.error(f"Question refinement error: {e}")
            return question
    
    async def generate_questions_streaming(
        self,
        gap: Gap,
        context: Optional[Dict] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream question generation for real-time updates
        """
        
        yield {"type": "progress", "message": "Analyzing gap context...", "progress": 0.1}
        
        # Build prompt
        prompt = await self._build_question_prompt(gap, context)
        
        yield {"type": "progress", "message": "Generating questions...", "progress": 0.3}
        
        # Stream LLM response
        async for chunk in self.llm.generate_stream(
            task_type="question_generation",
            prompt=prompt,
            context={"gap": gap.__dict__},
            max_tokens=2000,
            temperature=0.7
        ):
            yield {
                "type": "question_chunk",
                "content": chunk.get("content", ""),
                "progress": 0.5
            }
        
        yield {"type": "progress", "message": "Processing questions...", "progress": 0.8}
        
        # Generate final questions
        questions = await self.generate_questions(gap, context)
        
        yield {
            "type": "complete",
            "questions": [q.__dict__ for q in questions],
            "progress": 1.0,
            "total_questions": len(questions)
        }
    
    async def validate_question_quality(
        self,
        questions: List[Question]
    ) -> Dict[str, Any]:
        """
        Validate the quality of generated questions
        """
        
        questions_json = json.dumps([q.__dict__ for q in questions], indent=2)
        
        prompt = f"""
Evaluate the quality of these progressive disclosure questions:

{questions_json}

Rate each question on:
1. Clarity (1-10)
2. Specificity (1-10)
3. ESG relevance (1-10)
4. Progressive flow (1-10)

Return JSON:
{{
  "overall_score": 1-10,
  "questions": [
    {{
      "id": 1,
      "clarity": 8,
      "specificity": 7,
      "esg_relevance": 9,
      "progressive_flow": 8,
      "notes": "..."
    }}
  ],
  "recommendations": "..."
}}
"""
        
        try:
            response = await self.llm.generate(
                task_type="question_generation",
                prompt=prompt,
                max_tokens=1000,
                temperature=0.3
            )
            
            return json.loads(response["content"])
            
        except Exception as e:
            logger.error(f"Question validation error: {e}")
            return {"overall_score": 5, "questions": [], "recommendations": "Validation failed"}
