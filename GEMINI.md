# Global Workspace Rules & Behavioral Configuration

## Autonomous Execution Policy: Reduce Asking Permission to Continue
- **Act Proactively & Autonomously:** Do not pause or repeatedly ask for user permission, confirmation, or approval to continue ordinary analysis, code execution, or multi-step tasks.
- **Eliminate Confirmation Friction:** Avoid ending responses with passive questions like *"Would you like me to continue?"*, *"Shall I proceed with this?"*, or *"Do you want me to do this?"*. Instead, directly complete the work, provide the full solution, and execute the necessary actions.
- **Direct Delivery:** Provide deep, comprehensive, and complete answers immediately. Only stop to request user input if there is a severe destructive action (e.g., deleting critical data) or an unavoidable ambiguity that cannot be resolved through reasoning.

## Automated Stock List Archiving & Upgrade Quarantine Policy
- **Automatic Top-N Report Filing (`Stocks_Analysis_Report/`):** Whenever the user asks for a Top 10 / 15 / 25 (or any Top-N) stock list, automatically save the generated report inside the matching strategy subfolder under `Stocks_Analysis_Report/` (`Deadliest_Combo`, `Pre_Fly`, `Multibagger`, `Micro_Multibagger`, `SIP`, `Swing`, `Turnaround`, `Value_Buying`, `Comparison_And_Single`) using `save_stock_list_report()` from `app/services/research/report_archiver.py` with the naming format `<PREFIX>_TOP_<N>_<YYYY-MM-DD>_<HHMM_IST>.<md|pdf>`.
- **Zero Root Clutter & Upgrade Quarantine (`DELETION_REQUIRED/`):** Whenever temporary scripts, intermediate JSON dumps, or unnecessary files are generated during project upgrades or ad-hoc screening, keep them inside `DELETION_REQUIRED/` (or run `quarantine_unnecessary_files()` / `scripts/preflight_check.py`). Never delete any file inside `DELETION_REQUIRED/`.

