# Requirements NER Annotation Guidelines

## Labels

- `ACTOR`: The human, team, role, or system component responsible for performing the action.
  - Include the full noun phrase when it clearly names the performer.
  - Examples: `User`, `Admin`, `QA team`, `backend service`, `The system`.
- `ACTION`: The main requirement verb or verb phrase.
  - Prefer the smallest complete verb phrase.
  - Examples: `login`, `export`, `process`, `log in`, `sign up`.
- `FEATURE`: The functionality, module, artifact, or object acted on.
  - Include the smallest meaningful feature phrase after the action.
  - Examples: `dashboard`, `notifications service`, `payment gateway`, `audit log`.
- `CONSTRAINT`: Time, condition, trigger, frequency, or operating context.
  - Examples: `within 2 seconds`, `during peak hours`, `before next release`, `under heavy load`, `every day`.
- `QUALITY`: A non-functional characteristic or quality attribute expressed in the text.
  - Examples: `secure`, `reliable`, `fast`, `responsive`, `readable`, `available`.
- `PRIORITY`: Explicit urgency or severity markers.
  - Examples: `urgent`, `critical`, `ASAP`, `P0`, `P1`, `high priority`.

## Boundary Rules

- Use complete spans, not partial tokens.
- Do not include leading or trailing whitespace.
- Do not include punctuation unless it is part of the entity text.
- Do not create overlapping entities.
- When a phrase appears repeatedly, keep the same label everywhere unless the surrounding meaning clearly changes.

## Disambiguation Rules

- `FEATURE` vs `QUALITY`
  - Label the system artifact as `FEATURE`.
  - Label the property of that artifact as `QUALITY`.
  - Example: in `responsive dashboard`, `dashboard` is `FEATURE`, `responsive` is `QUALITY`.
- `CONSTRAINT` vs `PRIORITY`
  - `CONSTRAINT` limits when/how the requirement must hold.
  - `PRIORITY` signals urgency or triage status.
  - Example: `before Friday` is `CONSTRAINT`; `urgent` is `PRIORITY`.
- `ACTOR` vs `FEATURE`
  - If the phrase performs the verb, label it `ACTOR`.
  - If the phrase is acted upon, label it `FEATURE`.

## Quality Checks

- Validate that all spans align to the final cleaned text.
- Reject samples with overlapping spans.
- Flag phrases that receive multiple labels across the corpus.
- Review a 5-10% audit sample manually, prioritizing:
  - `QUALITY` vs `CONSTRAINT` edge cases
  - multi-clause sentences
  - noisy chat/email/Jira style text
  - sentences with more than three entities
