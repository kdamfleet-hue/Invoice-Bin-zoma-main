# Goal Description
The user wants to implement three main improvements:
1. **Dynamic Washing Report**: Apply a provided HTML design to 	emplates/washing_report.html and make it dynamic by wiring it to backend data.
2. **Fix Duplicate Plates**: Identify and resolve duplicate vehicles (e.g., 'د د و 4282') in the washing schedule data.
3. **Diagnostic JS Integration**: Integrate a provided JavaScript debugging snippet into the frontend to automatically monitor and diagnose missing localStorage data (especially the active branch).

## User Review Required
- The HTML provided for the washing report will replace the existing template 	emplates/washing_report.html. 
- The deduplication logic will automatically merge duplicate vehicles in the washing_schedule database blob by combining their wash counts.

## Open Questions
- Where exactly would you like the diagnostic JS alert to appear? Currently, I plan to run it silently in the Console, and if a critical issue (like missing ctiveBranch) is found, display a visual toast/alert to the user.

## Proposed Changes

### 1. Dynamic Washing Report Template
#### [MODIFY] 	emplates/washing_report.html
- Replace the current template with the user's provided HTML structure.
- Add Jinja variables (	otal_vehicles, 	otal_washes, month_amt, etc.) to the KPI cards and Finance Row.
- Use a {% for v in vehicles %} loop to generate the table rows dynamically.
- Implement the "Duplicate Plates Alert" section to appear dynamically based on the duplicate_plates variable.

### 2. Deduplication Logic
#### [MODIFY] outes/schedule.py
- In the washing_report() route, add a routine that detects duplicate plates.
- If duplicates exist, it will merge their records (summing the monthly washes array m), remove the duplicates, and save the cleaned data back to lob_set("washing_schedule", cleaned_data). 
- This ensures the database is permanently fixed simply by visiting the report page.

### 3. Diagnostic JS Integration
#### [MODIFY] 	emplates/base.html
- Inject the diagnostic JS script at the end of the <body>.
- Add logic so that if the ctiveBranch is missing from localStorage, it triggers a visual warning modal or toast, prompting the user to refresh or select a branch, thus preventing the "empty fleet indicators" issue.

## Verification Plan
### Automated Tests
- N/A
### Manual Verification
- Visit the /washing_report route and verify the new HTML styling is applied and populated with real data.
- Verify that duplicate plates disappear from the report and their wash counts are merged successfully.
- Clear localStorage in the browser console, refresh the page, and verify that the diagnostic script logs the results and shows a visual warning.
