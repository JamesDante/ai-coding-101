Parse the following outline and produce a structured curriculum JSON.

OUTLINE:
{{outline}}

Return this exact schema (JSON only):
{
  "topic": "string",
  "target_audience": "string",
  "chapters": [
    {
      "id": "string",            // e.g. "01-getting-started"
      "slug": "string",          // e.g. "getting-started"
      "title": "string",
      "description": "string",   // 1–2 sentences
      "category": "string|null", // group label, null = top-level
      "sidebar_position": 1,
      "difficulty": "beginner|intermediate|advanced",
      "estimated_minutes": 5
    }
  ]
}
