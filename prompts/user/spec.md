Create a detailed content spec for this chapter.

CHAPTER:
{{chapter}}

FULL CURRICULUM (for cross-reference context):
{{curriculum}}

Return this exact schema (JSON only):
{
  "chapter_id": "string",
  "title": "string",
  "slug": "string",
  "sidebar_position": 1,
  "category": "string|null",
  "difficulty": "string",
  "estimated_minutes": 5,
  "description": "string",          // 1 sentence — used as meta description
  "learning_objectives": ["string"],
  "prerequisites": ["string"],       // chapter slugs or prior knowledge phrases
  "sections": [
    {
      "heading": "string",
      "content_brief": "string",     // 2–3 sentences: exactly what to cover
      "has_code_example": true,
      "code_language": "string|null",
      "code_context": "string|null"  // what the example demonstrates
    }
  ],
  "key_terms": ["string"],
  "admonitions": [
    {
      "type": "tip|note|warning|info",
      "placement": "after_section_N",
      "content": "string"
    }
  ]
}
