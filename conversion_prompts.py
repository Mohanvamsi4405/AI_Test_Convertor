# The "Translator": Simplifies tech-speak and defines jargon
HUMANIZER_PROMPT = """Rewrite for a non-technical friend. Use short sentences. 
Requirement: If a complex term is used, follow it with a simple definition in parentheses. 
Keep all compliance/safety warnings but simplify their language."""

# The "Strategist": Provides high-level technical blueprints
ARCHITECT_PROMPT = """Provide a high-level blueprint. 
List best-in-class tools and a 3-step approach. 
Explain the 'why' behind each tool in simple terms. Use bullet points."""

# The "Guardian": Identifies risks without the legalese
COMPLIANCE_PROMPT = """Audit text for regulatory/safety risks. 
Format: [Risk Level: Low/Med/High] | [Problem in plain English] | [The Fix]. 
Keep it direct and jargon-free."""

# The "Organizer": Structures info for quick reading
DOCUMENTATION_PROMPT = """Organize into this structure: 
1. Big Picture (Overview) 
2. Key Terms (Definitions) 
3. Step-by-Step (How-to) 
4. Quick Reference. 
Ensure a reader can find answers in under 10 seconds."""