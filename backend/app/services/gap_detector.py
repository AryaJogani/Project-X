"""
AI-powered gap detection service
"""

from typing import List, Dict, Any, AsyncGenerator
import json
import asyncio
import logging
from datetime import datetime

from app.models.gap import Gap, GapType, GapSeverity
from app.models.document import Document

logger = logging.getLogger(__name__)

class GapDetectorService:
    """
    AI-powered gap detection service with multiple strategies
    """
    
    def __init__(self, llm_orchestrator):
        self.llm = llm_orchestrator
    
    async def detect_all_gaps(
        self,
        document: Document
    ) -> List[Gap]:
        """
        Detect all types of gaps in a document using parallel processing
        
        Args:
            document: Document to analyze
            
        Returns:
            List of detected gaps
        """
        
        logger.info(f"Starting gap detection for document: {document.title}")
        
        # Run multiple detection strategies in parallel
        tasks = [
            self.detect_structural_gaps(document),
            self.detect_semantic_gaps(document),
            self.detect_esg_gaps(document)
        ]
        
        # Execute concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and flatten results
        all_gaps = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Gap detection error: {result}")
            else:
                all_gaps.extend(result)
        
        # Merge and deduplicate using LLM
        merged_gaps = await self.merge_and_prioritize(all_gaps, document)
        
        logger.info(f"Detected {len(merged_gaps)} gaps for document: {document.title}")
        return merged_gaps
    
    async def detect_structural_gaps(
        self,
        document: Document
    ) -> List[Gap]:
        """
        Detect structural gaps (empty sections, incomplete tables)
        """
        
        prompt = f"""
Analyze the following document for structural gaps:
- Empty sections (headers with no content)
- Incomplete tables (missing cells)
- Missing required metadata
- Broken formatting

Document Title: {document.title}
Document Content:
{document.content}

Return a JSON list of gaps found, each with:
- type: "empty_section" | "incomplete_table" | "missing_metadata" | "broken_formatting"
- location: section or line number
- description: what's missing
- severity: "high" | "medium" | "low"

Format: {{"gaps": [...]}}
"""
        
        try:
            response = await self.llm.generate(
                task_type="gap_classification",
                prompt=prompt,
                max_tokens=2000,
                temperature=0.1  # Low temperature for factual analysis
            )
            
            # Parse LLM response into Gap objects
            gaps_data = json.loads(response["content"])
            gaps = []
            
            for gap_dict in gaps_data.get("gaps", []):
                gap = Gap(
                    document_id=document.id,
                    type=GapType.STRUCTURAL,
                    severity=GapSeverity(gap_dict.get("severity", "medium")),
                    location=gap_dict.get("location", "unknown"),
                    description=gap_dict.get("description", ""),
                    context={"detection_method": "structural", "raw_data": gap_dict}
                )
                gaps.append(gap)
            
            return gaps
            
        except Exception as e:
            logger.error(f"Structural gap detection error: {e}")
            return []
    
    async def detect_semantic_gaps(
        self,
        document: Document
    ) -> List[Gap]:
        """
        Detect semantic gaps (shallow content, undefined terms)
        """
        
        prompt = f"""
Analyze this ESG document for semantic issues:
- Shallow explanations (lacking depth)
- Undefined technical terms and acronyms
- Vague statements needing specifics
- Missing examples or evidence
- Incomplete reasoning or logic

Document Title: {document.title}
Document Content:
{document.content}

Identify gaps where content is present but insufficient or unclear.

Return JSON: {{"gaps": [...]}}
Each gap should have:
- type: "shallow_explanation" | "undefined_term" | "vague_statement" | "missing_evidence"
- location: section or line number
- description: what's missing or unclear
- severity: "high" | "medium" | "low"
"""
        
        try:
            response = await self.llm.generate(
                task_type="gap_analysis_deep",
                prompt=prompt,
                max_tokens=3000,
                temperature=0.3
            )
            
            gaps_data = json.loads(response["content"])
            gaps = []
            
            for gap_dict in gaps_data.get("gaps", []):
                gap = Gap(
                    document_id=document.id,
                    type=GapType.SEMANTIC,
                    severity=GapSeverity(gap_dict.get("severity", "medium")),
                    location=gap_dict.get("location", "unknown"),
                    description=gap_dict.get("description", ""),
                    context={"detection_method": "semantic", "raw_data": gap_dict}
                )
                gaps.append(gap)
            
            return gaps
            
        except Exception as e:
            logger.error(f"Semantic gap detection error: {e}")
            return []
    
    async def detect_esg_gaps(
        self,
        document: Document
    ) -> List[Gap]:
        """
        Detect ESG framework compliance gaps
        """
        
        prompt = f"""
Analyze this document for ESG framework compliance:
- Missing GRI (Global Reporting Initiative) disclosures
- Missing SASB (Sustainability Accounting Standards Board) metrics
- Missing TCFD (Task Force on Climate-related Financial Disclosures) recommendations
- Incomplete sustainability reporting
- Missing governance disclosures

Document Title: {document.title}
Document Content:
{document.content}

Identify what's required by ESG frameworks but missing in the document.

Return JSON: {{"gaps": [...]}}
Each gap should have:
- type: "missing_gri" | "missing_sasb" | "missing_tcfd" | "incomplete_reporting"
- location: section or line number
- description: what ESG requirement is missing
- severity: "high" | "medium" | "low"
"""
        
        try:
            response = await self.llm.generate(
                task_type="gap_analysis_deep",
                prompt=prompt,
                max_tokens=3000,
                temperature=0.2
            )
            
            gaps_data = json.loads(response["content"])
            gaps = []
            
            for gap_dict in gaps_data.get("gaps", []):
                gap = Gap(
                    document_id=document.id,
                    type=GapType.ESG_COMPLIANCE,
                    severity=GapSeverity(gap_dict.get("severity", "medium")),
                    location=gap_dict.get("location", "unknown"),
                    description=gap_dict.get("description", ""),
                    context={"detection_method": "esg_compliance", "raw_data": gap_dict}
                )
                gaps.append(gap)
            
            return gaps
            
        except Exception as e:
            logger.error(f"ESG gap detection error: {e}")
            return []
    
    async def merge_and_prioritize(
        self,
        gaps: List[Gap],
        document: Document
    ) -> List[Gap]:
        """
        Use LLM to deduplicate and prioritize gaps
        """
        
        if not gaps:
            return []
        
        gaps_json = json.dumps([gap.__dict__ for gap in gaps], indent=2)
        
        prompt = f"""
You have detected multiple gaps across different analysis strategies.
Some may be duplicates or overlapping.

Document: {document.title}
Gaps:
{gaps_json}

Tasks:
1. Remove duplicate gaps (same issue detected multiple times)
2. Merge overlapping gaps into single comprehensive gaps
3. Prioritize by severity and ESG framework importance
4. Return deduplicated, prioritized list

Return JSON: {{"gaps": [...]}}
Each gap should have:
- type: gap type
- severity: "high" | "medium" | "low"
- location: section or line number
- description: comprehensive description
- priority_score: 1-10 (10 being highest priority)
"""
        
        try:
            response = await self.llm.generate(
                task_type="gap_classification",
                prompt=prompt,
                max_tokens=4000,
                temperature=0.2
            )
            
            merged_data = json.loads(response["content"])
            merged_gaps = []
            
            for gap_dict in merged_data.get("gaps", []):
                # Create new gap with merged information
                gap = Gap(
                    document_id=document.id,
                    type=GapType(gap_dict.get("type", "structural")),
                    severity=GapSeverity(gap_dict.get("severity", "medium")),
                    location=gap_dict.get("location", "unknown"),
                    description=gap_dict.get("description", ""),
                    context={
                        "detection_method": "merged",
                        "priority_score": gap_dict.get("priority_score", 5),
                        "merged_from": len(gaps)
                    }
                )
                merged_gaps.append(gap)
            
            # Sort by priority score
            merged_gaps.sort(key=lambda g: g.context.get("priority_score", 5), reverse=True)
            
            return merged_gaps
            
        except Exception as e:
            logger.error(f"Gap merging error: {e}")
            return gaps  # Return original gaps if merging fails
    
    async def detect_gaps_streaming(
        self,
        document: Document
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream gap detection results as they're found
        """
        
        logger.info(f"Starting streaming gap detection for: {document.title}")
        
        # Structural gaps (fast)
        yield {"type": "progress", "message": "Detecting structural gaps...", "progress": 0.1}
        structural_gaps = await self.detect_structural_gaps(document)
        for gap in structural_gaps:
            yield {"type": "gap_detected", "gap": gap.__dict__, "progress": 0.3}
        
        # Semantic gaps (slower)
        yield {"type": "progress", "message": "Detecting semantic gaps...", "progress": 0.4}
        semantic_gaps = await self.detect_semantic_gaps(document)
        for gap in semantic_gaps:
            yield {"type": "gap_detected", "gap": gap.__dict__, "progress": 0.6}
        
        # ESG gaps (slowest)
        yield {"type": "progress", "message": "Detecting ESG compliance gaps...", "progress": 0.7}
        esg_gaps = await self.detect_esg_gaps(document)
        for gap in esg_gaps:
            yield {"type": "gap_detected", "gap": gap.__dict__, "progress": 0.8}
        
        # Final merge
        yield {"type": "progress", "message": "Merging and prioritizing gaps...", "progress": 0.9}
        all_gaps = structural_gaps + semantic_gaps + esg_gaps
        merged_gaps = await self.merge_and_prioritize(all_gaps, document)
        
        yield {
            "type": "complete",
            "gaps": [gap.__dict__ for gap in merged_gaps],
            "progress": 1.0,
            "total_gaps": len(merged_gaps)
        }
