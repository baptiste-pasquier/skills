# {{Project}} at a glance

{{One paragraph. Who uses the product, what it does for them, and the one architectural fact
a reader must hold before anything else, such as "deterministic code prepares the request,
one model writes the reply, and code closes it".}}

**Legend:** {{one sentence per class, from `conventions/documentation.md`, for example: red
for an LLM call, yellow for text the model writes to the user, blue for deterministic
code}}.

## Where {{Project}} runs

```mermaid
flowchart TB
    user([User]) --> entry["Front end"]
    entry --> app["Application"]
    subgraph external["External services"]
        direction LR
        api1["Service A"]
        api2["Service B"]
    end
    app --> external

    classDef code fill:#e8f0fe,stroke:#1a73e8,color:#000
    class entry,app code
    style external fill:none,stroke:#888
```

## The user's journey

```mermaid
flowchart TD
    start(["Entry point"]) -->|"choice A"| stepA["Step A"]
    start -->|"choice B"| stepB["Step B"]
    stepA --> done(["Outcome"])
    stepB --> done

    classDef code fill:#e8f0fe,stroke:#1a73e8,color:#000
    class stepA,stepB code
```

## One {{request / turn / job}}

<!-- {{unit}}-diagram -->

```mermaid
flowchart TD
    input([Input]) --> first["first_step"]
    first --> second["second_step"]
    second --> output([Output])

    classDef code fill:#e8f0fe,stroke:#1a73e8,color:#000
    class first,second code
```

## Features

<div class="grid cards" markdown>

- **{{[Feature](explanation/feature.md)}}**

    {{Two lines: what the feature does, and the question this page answers.}}

- **[Code map](reference/code-map.md)**

    Where each package lives, and the file to open to change a text, a rule or a
    threshold.

</div>

**New here?** {{Read the deep dives in this order: 1 [first](explanation/first.md) →
2 [second](explanation/second.md) → 3 [third](explanation/third.md).}}

## All pages

{{WITHOUT A SITE ONLY. With a site, the `nav` of `zensical.toml` is the index: delete this
section.}}

Every maintained doc is listed here, and a doc missing from the list fails CI.

- `explanation/`: {{[feature](explanation/feature.md)}}
- `how-to/`: {{[do a thing](how-to/do-a-thing.md)}}
- `reference/`: [code map](reference/code-map.md)
- `conventions/`: [documentation](conventions/documentation.md)

Writing a page? The rules are in [`conventions/documentation.md`](conventions/documentation.md).
