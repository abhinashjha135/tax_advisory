# Tax Advisor Application – Phase 2: PDF Upload, Extraction, and Manual Data Review (DRAFT)

## Overview
This document outlines the requirements and deliverables for **Phase 2** of the Tax Advisor Application. The goal of this phase is to enable users to upload their Pay Slip or Form 16 (PDF), extract relevant financial data, and review/edit the extracted data in a user-friendly form.

---

## Phase 2 Scope

### 1. PDF Upload
- Users can upload a Pay Slip or Form 16 (PDF) via the frontend interface.
- The uploaded PDF is sent to the backend for processing.

### 2. Data Extraction
- The backend processes the uploaded PDF using:
  - `PyPDF2` for text extraction from digital PDFs.
  - `pytesseract` for OCR on scanned/image-based PDFs.
  - Google Gemini LLM to structure and validate the extracted data.
- Extracted data includes all fields required for tax calculation (see Phase 1 `UserFinancials` schema).

### 3. Data Review & Edit Form
- The frontend displays a form pre-filled with the extracted data.
- Users can review and manually edit any field before proceeding.

### 4. Tax Regime Selection
- The form includes a radio button for the user to select their preferred tax regime (Old/New).

---

## User Flow
1. User lands on the application and clicks "Start".
2. User is prompted to upload a Pay Slip or Form 16 (PDF).
3. The PDF is uploaded to the backend and processed for data extraction.
4. Extracted data is returned and displayed in a pre-filled form.
5. User reviews/edits the data and selects a tax regime.
6. User submits the verified data to proceed to the next phase.

---

## Technical Requirements
- **Frontend:**
  - PDF upload UI component.
  - Data review/edit form with all required fields.
  - Tax regime selection (radio button).
- **Backend:**
  - Endpoint to receive and temporarily store the uploaded PDF.
  - PDF processing pipeline using PyPDF2, pytesseract, and Gemini LLM.
  - Return structured data to the frontend for review.
  - Ensure temporary PDF files are deleted after processing.

---

## Acceptance Criteria
- [ ] User can upload a PDF (Pay Slip or Form 16).
- [ ] Extracted data is shown in a pre-filled, editable form.
- [ ] User can review and edit all fields.
- [ ] User can select a tax regime (Old/New).
- [ ] Temporary PDF files are deleted after processing.

---

## References
- [Master PRD (PRD_V001.md)](../PRD_V001.md)
- [Phase 1 PRD (PHASE1.md)](./PHASE1.md)

---

**Please review this draft PRD for Phase 2 and let me know if any changes or additions are needed before finalization.** 