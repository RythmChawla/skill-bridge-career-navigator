# Design Notes

## Problem Framing

The goal is to help a learner understand:

- what role they are currently closest to
- which skills they already have
- which skills they still need
- what to learn next in a realistic order

The product is designed around one clear user journey instead of many loosely connected screens.

## Main Flow

1. User signs up or signs in
2. User uploads a resume
3. Backend extracts resume text and structures it into profile data
4. User reviews and edits profile sections
5. App recommends top 3 matching roles from the dataset
6. User runs gap analysis for a target role
7. App shows missing skills, proficiency, feedback, and roadmap

## Why The Architecture Is Split This Way

### Rule-based logic

These parts are deterministic and happen locally:

- deduplicating roles from the CSV
- matching user skills vs role skills
- computing missing skills and proficiency
- ranking top job-role matches

This keeps the core analysis explainable and stable.

### AI-assisted logic

These parts use the LLM:

- converting raw resume text into structured sections
- generating personalized narrative feedback
- generating a teacher-style roadmap

This gives flexibility where natural language is valuable, while preserving deterministic scoring underneath.

## Data Design

Each profile stores:

- name
- target role
- skills
- resume text
- resume path
- contact fields
- socials
- education
- experience
- projects

These sections are stored in structured form so the frontend can edit them independently.

## UX Decisions

- Auth is the first screen to make the flow feel like one learner workspace
- Profile editing is section-by-section rather than one giant form
- Resume viewing is separate from resume uploading/updating
- Top matches are shown early so users immediately see value after upload
- Skill gap analysis remains focused on one role at a time

## Responsible AI Decisions

- Synthetic job data only
- User-correctable extraction results
- Fallback text if the LLM is unavailable
- Core scoring does not depend on the LLM

## What Was Intentionally Left Simple

- SQLite instead of a production database
- no background jobs
- no advanced auth hardening
- no versioned profile history
- no migration tooling

These were reasonable tradeoffs for the prototype scope and timebox.
