#!/usr/bin/env bash
set -euo pipefail

SOP_URL="https://raw.githubusercontent.com/bmw-ece-ntust/SOP/master/project-documentation.md"
OUT_DIR="docs/upstream"
OUT_FILE="$OUT_DIR/SOP-project-documentation.md"

mkdir -p "$OUT_DIR"

echo "Downloading SOP template: $SOP_URL"
curl -fsSL "$SOP_URL" -o "$OUT_FILE"

echo "Saved to: $OUT_FILE"
echo
cat <<'EOF'
Next steps:
- Review diffs vs README.md:
    git --no-pager diff -- README.md "$OUT_FILE" || true
- Use SOP as the source-of-truth reference, then update README.md sections accordingly.

Note:
- This script fetches upstream content at runtime; it does not embed SOP content in this repository.
EOF
