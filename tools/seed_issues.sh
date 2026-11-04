#!/usr/bin/env bash
# Seed ~50 clean-house issues: 3 labels, 1 milestone, issues across 3 categories.
# Requires: gh authenticated, run from the repo root.
set -euo pipefail

echo "Creating labels..."
gh label create deprecated-api --color D93F0B --description "Deprecated scikit-image API in wrapper" --force
gh label create weak-tests     --color FBCA04 --description "Missing or assertion-free wrapper test" --force
gh label create boundary       --color 1D76DB --description "Import outside the wrapper boundary" --force

MILESTONE="Clean House - Round 1"
echo "Ensuring milestone: $MILESTONE"
if ! gh api "repos/{owner}/{repo}/milestones?state=all" --jq '.[].title' | grep -qxF "$MILESTONE"; then
  gh api "repos/{owner}/{repo}/milestones" -f title="$MILESTONE" \
    -f description="First pass of library tech-debt cleanup under the convention gate." >/dev/null
fi

# feature nouns to template realistic titles
FEATURES=(sharpen denoise segment resize_safe deskew threshold_adaptive \
  gamma_correct unsharp_mask edge_overlay histogram_match tophat white_balance \
  clahe_tiles vignette_fix median_stack contrast_stretch rolling_ball)

mk () { # category label  title
  gh issue create --title "$2" --label "$1" --milestone "$MILESTONE" \
    --body "$3" >/dev/null && echo "  + [$1] $2"
}

echo "Creating deprecated-api issues..."
i=0
for f in "${FEATURES[@]}"; do
  i=$((i+1)); [ $i -gt 17 ] && break
  if [ $i -eq 1 ]; then
    mk deprecated-api "[LIVE DEMO] Replace deprecated multichannel= in wrapper/${f}" \
      "The \`${f}\` wrapper calls a scikit-image function with the deprecated \`multichannel=\` keyword. Replace it with \`channel_axis=\` and keep the test green. This is the change demoed live."
  else
    mk deprecated-api "Replace deprecated call in wrapper/${f}" \
      "wrapper/${f} uses a deprecated scikit-image API. Move to the current public API; the CI gate must pass on the diff."
  fi
done

echo "Creating weak-tests issues..."
i=0
for f in "${FEATURES[@]}"; do
  i=$((i+1)); [ $i -gt 17 ] && break
  mk weak-tests "Strengthen weak test for wrapper/${f}" \
    "tests/test_${f}.py runs the function but asserts nothing. Add assertions covering shape, value range, and an edge case."
done

echo "Creating boundary issues..."
i=0
for f in "${FEATURES[@]}"; do
  i=$((i+1)); [ $i -gt 16 ] && break
  mk boundary "Remove out-of-boundary import in wrapper/${f}" \
    "wrapper/${f} imports a private \`skimage._*\` module or a non-whitelisted library. Re-express via an approved module or extend core.public in a separate change."
done

echo "Done. Issue count:"
gh issue list --state open --limit 100 --json number --jq 'length'
