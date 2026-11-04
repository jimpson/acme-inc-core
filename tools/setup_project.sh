#!/usr/bin/env bash
# Create a public GitHub Project board, add a Category field, and add all open
# issues. Requires: gh authenticated with 'project' scope. Run from repo root.
set -euo pipefail

TITLE="Acme Clean House"
OWNER=$(gh api user --jq .login)

echo "Creating project '$TITLE' for @$OWNER ..."
NUM=$(gh project create --owner "@me" --title "$TITLE" --format json --jq '.number')
echo "project number: $NUM"

echo "Adding single-select Category field..."
gh project field-create "$NUM" --owner "@me" --name "Category" \
  --data-type SINGLE_SELECT \
  --single-select-options "deprecated-api,weak-tests,boundary" >/dev/null

echo "Making project public..."
gh project edit "$NUM" --owner "@me" --visibility PUBLIC >/dev/null

echo "Adding open issues to the board..."
gh issue list --state open --limit 100 --json url --jq '.[].url' | while read -r url; do
  gh project item-add "$NUM" --owner "@me" --url "$url" >/dev/null && echo "  + $url"
done

echo "Project URL:"
gh project view "$NUM" --owner "@me" --format json --jq '.url'
