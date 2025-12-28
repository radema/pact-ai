# PACT-AI Whitepaper

Protocol for Agent Control & Trust

## Executive Summary

PACT-AI is a repository-native governance protocol designed for Software Engineering 3.0 (SE 3.0). As development shifts from human-authored code to AI-generated implementation, the critical bottleneck moves from "Writing Speed" to "Trust & Verification."

PACT goal is to implement a strict AI-DLC (AI Development Life Cycle) by enforcing a "Filesystem Sovereignty" model. It prevents "Agent Drift"—where AI diverts from the original intent—by requiring cryptographic seals on specifications before any implementation occurs.

## The Role Architecture

Aligning with modern Agentic patterns, PACT defines a default team of five specialized agents to ensure separation of concerns:

* The Spec Writer (Requirement Engineering): Translates ambiguity into rigid Gherkin-style intent.

* The Architect (DOMA Gatekeeper): Ensures new features respect domain boundaries and do not introduce structural debt.

* The Developer (Implementation): A narrow-focus agent that executes the sealed plan.

* The Doc Writer (Knowledge Management): Ensures the codebase remains intelligible to humans and future agents.

* The QA Engineer (Verification): The ultimate gatekeeper, validating that implementation matches the intent (MRP).

## The Core Axioms

1. **Protocol over Platform**: PACT is not a SaaS. It is a local protocol defined by file structures (.pacts/).

2. **No Action Without Seal**: Execution is cryptographically blocked until the Blueprint (02_specs.md) is approved.

3. **Separation of Infrastructure & Intellect**: Model configurations (models.yaml) are decoupled from Agent definitions (agents.yaml).

## The Architecture

PACT operates on a "Steering & Engine" model:

1. The Steering (PACT CLI): A Python-based governance tool that manages the lifecycle of "Bolts" (Units of Work).

2. The Engine (IDE Agent): Your existing AI tool (Antigravity, Cursor, Jules, etc.) acts as the runtime, reading PACT's state to determine its allowed actions.

## Conclusion

PACT provides the "Guardrails" for the AI era. It allows organizations to adopt autonomous agents while maintaining the strict auditability and quality standards required by enterprise software engineering.
