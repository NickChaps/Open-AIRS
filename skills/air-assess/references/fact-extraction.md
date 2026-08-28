# Fact extraction protocol

1. Quote or point to the smallest source location that supports the fact.
2. Distinguish declaration, document, configuration, observation and inference.
3. Use `known` only when the source establishes a value.
4. Use `unknown` when the source is silent or too vague.
5. Use `conflicted` when credible sources disagree; retain every source.
6. Attach confidence to model inferences, not to deterministic rule results.
7. Record the extraction model, prompt or skill version in the `extractor`
   metadata when an LLM produced the fact.
8. Treat security guidelines in a prompt as instructions, not proof that a
   technical gate exists.
9. Treat connector availability, permission, planned invocation and observed
   execution as different facts.
10. Ask for review when a legal element depends on ambiguous language.
