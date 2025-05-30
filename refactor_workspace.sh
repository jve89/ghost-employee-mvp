#!/bin/bash

echo "🚧 Starting safe refactor of Ghost Employee workspace..."

# Step 1: Create target directory structure
mkdir -p ghost_employee/{inputs,outputs,processing,queue,ai_modules,core,dashboard/routes,dashboard/tiles,logs,config}
mkdir -p archive/{legacy,scripts,tools}

# Step 2: Move + Rename core modules
mv src/inputs/* ghost_employee/inputs/
mv src/outputs/notion_exporter.py ghost_employee/outputs/
mv src/outputs/sheets_exporter.py ghost_employee/outputs/
mv src/outputs/export_manager.py ghost_employee/outputs/
mv src/outputs/log_manager.py ghost_employee/outputs/
mv src/outputs/log_watcher.py ghost_employee/outputs/
mv src/outputs/email_sender.py ghost_employee/outputs/
mv src/processing/summary_analyser.py ghost_employee/processing/
mv src/processing/task_extractor.py ghost_employee/processing/
mv src/processing/task_executor.py ghost_employee/processing/
mv src/processing/template_filler.py ghost_employee/processing/
mv src/processing/report_generator.py ghost_employee/processing/summary_report_generator.py
mv src/processing/email_responder.py archive/
mv retry_worker.py ghost_employee/queue/
mv queue_utils.py ghost_employee/queue/
mv patch_retry_ids.py archive/
mv auto_scheduler.py ghost_employee/core/
mv slack_debug.py archive/tools/
mv slack_debug_channels.py archive/tools/
mv scripts/* archive/scripts/

# Step 3: Dashboard routes and tiles
mv api/retry_controls.py ghost_employee/dashboard/routes/
mv dashboard/job_logs_api.py ghost_employee/dashboard/routes/
mv dashboard/tiles/dead_tasks.py ghost_employee/dashboard/tiles/task_health_dead.py
mv dashboard/tiles/stale_tasks.py ghost_employee/dashboard/tiles/task_health_stale.py
mv dashboard/tiles/export_summary.py ghost_employee/dashboard/tiles/summary_tile.py
mv dashboard/tiles/retry_delays.py ghost_employee/dashboard/tiles/retry_summary.py

# Step 4: Core runner logic
mv src/controller.py ghost_employee/core/
mv src/core_runner.py ghost_employee/core/
mv src/job_loader.py ghost_employee/core/
mv src/job_runner.py ghost_employee/core/
mv src/main.py ghost_employee/app_main.py

# Step 5: Move misc tools + loggers
mv logstore/history_logger.py ghost_employee/logs/

# Step 6: Move AI modules
mv modules/role_inferencer.py ghost_employee/ai_modules/
mv src/processing/gpt_classifier.py ghost_employee/ai_modules/
mv src/processing/due_date_extractor.py ghost_employee/ai_modules/
mv src/processing/time_slot_parser.py ghost_employee/ai_modules/
mv src/processing/user_mapper.py ghost_employee/ai_modules/

# Step 7: Archive unused or legacy code
mv legacy/legacy_email_listener.py archive/legacy/
mv generate_sample_docx.py archive/
mv generate_sample_pdf.py archive/
mv generate_sample_xlsx.py archive/
mv run_test_save.py archive/

# Step 8: Optional cleanup
echo "🧹 Done moving files. You can now:"
echo "- Update imports in files under ghost_employee/"
echo "- Delete 'src/' and 'modules/' once you're confident"
echo "- Manually test FastAPI + job runners"

echo "✅ Refactor complete. Your codebase is now modular and safe."
