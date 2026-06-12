Review this MDX documentation page against its spec.

SPEC:
{{spec}}

DOCUMENT:
{{doc}}

Return this exact schema (JSON only):
{
  "chapter_id": "string",
  "score": 8,
  "needs_fix": false,
  "issues": [
    {
      "severity": "error|warning|suggestion",
      "location": "string",
      "description": "string",
      "fix": "string"
    }
  ],
  "strengths": ["string"]
}

Set needs_fix: true if score < {{threshold}}.
