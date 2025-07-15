# Phase 4: Gemini-powered Advisor (Q&A, Suggestions)

## Objective
Enable users to receive smart, contextual follow-up questions and personalized, actionable investment and tax-saving suggestions powered by the Gemini LLM, based on their submitted financial data.

## User Stories
- As a user, I want the system to ask me a relevant follow-up question after I submit my tax data.
- As a user, I want to answer the question and receive personalized, AI-powered investment and tax-saving suggestions.
- As a user, I want the suggestions to be clear, actionable, and easy to understand.

## Features
- Backend integration with Gemini LLM to generate follow-up questions and suggestions.
- Store user answers and AI suggestions in the database, linked to the session ID.
- Frontend UI for:
  - Displaying the follow-up question.
  - Accepting the user's answer.
  - Displaying the AI-generated suggestions in a modern, readable card format.
- Error handling and graceful fallback if the AI service is unavailable.

## Backend Requirements
- Implement `/api/chat` endpoint:
  - Accepts session_id and user answer.
  - Uses Gemini LLM to generate personalized suggestions based on all user data and the answer.
  - Returns suggestions as structured JSON (e.g., list of cards or bullet points).
  - Stores the question, answer, and suggestions in the database.
- Ensure all secrets and API keys are securely managed.

## Frontend Requirements
- After tax comparison, display the follow-up question from the backend.
- Allow the user to submit their answer.
- Display the AI-generated suggestions in a visually appealing card format.
- Provide a way to return to previous steps or start a new session.

## Acceptance Criteria
- User receives a relevant follow-up question after tax calculation.
- User can submit an answer and receive personalized suggestions.
- Suggestions are clear, actionable, and visually distinct.
- All interactions are stored in the database with the session ID.
- Errors are handled gracefully and communicated to the user.

## Notes
- Use the Gemini LLM for both question generation and suggestions.
- Ensure the UI/UX is consistent with previous phases.
- Prepare for future enhancements, such as multi-turn conversations or admin analytics. 