# Phase 3: Tax Calculation Engine & Regime Comparison UI

## Objective
Enable users to view a clear, side-by-side comparison of their tax liabilities under both the Old and New tax regimes, based on their provided/verified financial data. Ensure the calculated data is saved to the database for future reference.

## User Stories
- As a user, I want to see my tax calculated for both regimes so I can make an informed choice.
- As a user, I want the UI to clearly highlight the regime I select.
- As a user, I want my financial data and calculation results to be saved securely.

## Features
- Tax calculation logic for both Old and New regimes (FY 2024-25 slabs).
- Backend endpoint to receive user data and return tax calculations for both regimes.
- UI: Two visually distinct cards showing Old vs. New regime results, with the selected regime highlighted.
- Save all relevant data and results to the Supabase database with a unique session ID.
- Error handling for invalid or incomplete data.

## Backend Requirements
- Implement `/api/calculate-tax` endpoint:
  - Accepts user financial data (session_id, salary components, deductions, regime selection).
  - Calculates tax for both regimes using the correct slabs and deductions.
  - Returns a JSON response with detailed breakdowns for both regimes.
  - Saves the calculation results to the `UserFinancials` table in Supabase.
- Ensure all calculations use the latest FY 2024-25 rules (see Appendix A).

## Frontend Requirements
- After user reviews/edits their data and selects a regime, submit to `/api/calculate-tax`.
- Display two cards: one for Old Regime, one for New Regime.
- Highlight the user's selected regime.
- Show breakdown: gross income, deductions, taxable income, tax, cess, total liability.
- Provide a clear call-to-action to proceed to the AI-powered advisor (Phase 4).

## Acceptance Criteria
- User sees both regimes' tax calculations in a clear, side-by-side UI.
- User's selected regime is visually highlighted.
- All calculation data is saved to the database with the session ID.
- Calculations match the FY 2024-25 rules in Appendix A.
- Errors are handled gracefully and communicated to the user.

## Notes
- Use the tax slab and deduction logic as detailed in Appendix A.
- Ensure the UI is responsive and visually consistent with previous phases.
- Prepare for integration with the AI-powered advisor in Phase 4. 