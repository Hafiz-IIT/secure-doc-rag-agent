# Architecture

```mermaid
flowchart LR
    A0[documents/chunks] --> A1
    A1[access filter] --> A2
    A2[query tokenization] --> A3
    A3[retrieval scoring] --> A4
    A4[ranked hits] --> A5
    A5[evidence packet] --> A6
    A6[sufficiency gate]
```

## Chunk model
Stores source, text, sensitivity, provenance, and stable chunk ID.

## Access layer
Excludes chunks outside the caller's allowed sensitivity set.

## Retriever
Scores query/chunk token overlap and returns ranked traceable hits.

## Evidence gate
Marks the packet insufficient when the minimum number of hits is not reached.

## Principle
Retrieval should return an inspectable evidence object, not silently convert search results into permission to act.
