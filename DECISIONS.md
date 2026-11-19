
## ADR-002: Initial LLM Selection

### Decision
Use GPT-4.1-mini as the initial model for QueryMind AI.

### Reasons
- Lower-cost development and experimentation
- Suitable candidate for instruction-following tasks
- Supports structured outputs
- Integrates easily with the OpenAI Python SDK
- Allows us to focus on the Text-to-SQL architecture

### Trade-offs
- May struggle with complex SQL reasoning
- Accuracy has not yet been benchmarked
- Depends on an external API provider

### Future Evaluation
Compare models using:
- SQL execution accuracy
- Clarification accuracy
- Response latency
- Cost per request

### Status
Provisional — pending evaluation
