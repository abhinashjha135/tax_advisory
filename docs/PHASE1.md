# Tax Advisor Application – Phase 1: Project Setup, DB Schema, and Landing Page

## Overview
This document outlines the requirements and deliverables for **Phase 1** of the Tax Advisor Application, as described in the master PRD. The goal of this phase is to establish the project foundation, set up the database schema, and implement a modern landing page.

---

## Phase 1 Scope

### 1. Project Setup
- Initialize the project repository (structure for frontend and backend).
- Set up version control (GitHub recommended).
- Prepare environment for local development (virtual environment, dependencies, etc.).

### 2. Database Schema (Supabase)
- Create the `UserFinancials` table in Supabase with the following columns:

| Column Name           | Data Type         | Description                          |
|----------------------|------------------|--------------------------------------|
| `session_id`         | UUID             | Primary Key, unique session identifier|
| `gross_salary`       | NUMERIC(15, 2)   | Total gross salary                   |
| `basic_salary`       | NUMERIC(15, 2)   | Basic salary component               |
| `hra_received`       | NUMERIC(15, 2)   | HRA received                         |
| `rent_paid`          | NUMERIC(15, 2)   | Annual rent paid                     |
| `deduction_80c`      | NUMERIC(15, 2)   | 80C investments                      |
| `deduction_80d`      | NUMERIC(15, 2)   | 80D medical insurance                |
| `standard_deduction` | NUMERIC(15, 2)   | Standard deduction                   |
| `professional_tax`   | NUMERIC(15, 2)   | Professional tax paid                |
| `tds`                | NUMERIC(15, 2)   | Tax Deducted at Source               |
| `created_at`         | TIMESTAMPTZ      | Record creation timestamp            |

- Ensure the table is accessible from the backend (Python, psycopg2).

### 3. Landing Page
- Implement a modern, branded landing page as the application's entry point.
- Design requirements:
  - Clean, light theme with blue highlights.
  - Use "Aptos Display" font for typography.
  - Prominent "Start" button to begin the user flow.
  - Responsive and visually appealing layout.

---

## Acceptance Criteria
- [ ] The project repository is initialized and structured for both frontend and backend development.
- [ ] The `UserFinancials` table exists in Supabase with the specified schema.
- [ ] The landing page is accessible, visually matches the design requirements, and includes a working "Start" button.

---

## References
- [Master PRD (PRD_V001.md)](../PRD_V001.md)
- [Supabase Documentation](https://supabase.com/docs)
- [Aptos Display Font](https://learn.microsoft.com/en-us/typography/font-list/aptos) 