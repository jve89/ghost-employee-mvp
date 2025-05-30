#!/bin/bash

# Root folder containing your Python packages
ROOT="ghost_employee"

# Find all Python files
FILES=$(find $ROOT -name "*.py")

# Mapping of import prefixes to correct fully qualified imports
declare -A replacements=(
  ["from dashboard"]="from ghost_employee.dashboard"
  ["import dashboard"]="import ghost_employee.dashboard"

  ["from core"]="from ghost_employee.core"
  ["import core"]="import ghost_employee.core"

  ["from queue"]="from ghost_employee.queue"
  ["import queue"]="import ghost_employee.queue"

  ["from scheduler"]="from ghost_employee.scheduler"
  ["import scheduler"]="import ghost_employee.scheduler"

  ["from logstore"]="from ghost_employee.logstore"
  ["import logstore"]="import ghost_employee.logstore"

  ["from outputs"]="from ghost_employee.outputs"
  ["import outputs"]="import ghost_employee.outputs"

  ["from ai_modules"]="from ghost_employee.ai_modules"
  ["import ai_modules"]="import ghost_employee.ai_modules"
)

for f in $FILES; do
  for old in "${!replacements[@]}"; do
    new=${replacements[$old]}
    sed -i "s|$old|$new|g" "$f"
  done
done

echo "All imports rewritten to use full 'ghost_employee' package prefixes."
