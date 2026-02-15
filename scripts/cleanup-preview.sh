#!/usr/bin/env bash
set -e

PR_NUMBER="$1"

echo "🧹 Cleaning up preview for PR #$PR_NUMBER..."

# If the folder does not exist, exit without error
if [ ! -d "pr-$PR_NUMBER" ]; then
  echo "ℹ️  No preview found for PR #$PR_NUMBER"
  exit 0
fi

# Delete folder
rm -rf "pr-$PR_NUMBER"
echo "✅ Removed pr-$PR_NUMBER directory"

# Allow glob to not fail if there are no matches
shopt -s nullglob

# Configure git
git config user.name "github-actions[bot]"
git config user.email "github-actions[bot]@users.noreply.github.com"

# Dynamically regenerate index.html
{
  echo '<!DOCTYPE html>'
  echo '<html>'
  echo '<head>'
  echo '  <title>PR Previews</title>'
  echo '  <meta charset="UTF-8">'
  echo '  <style>'
  echo '    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; }'
  echo '    h1 { color: #333; }'
  echo '    ul { list-style: none; padding: 0; }'
  echo '    li { background: white; margin: 10px 0; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }'
  echo '    a { color: #1976d2; text-decoration: none; font-weight: 500; }'
  echo '    a:hover { text-decoration: underline; }'
  echo '  </style>'
  echo '</head>'
  echo '<body>'
  echo '  <h1>📄 Pull Request Previews</h1'
  echo '  <ul>'

  for dir in pr-*; do
    [ -d "$dir" ] || continue
    PR_NUM="${dir#pr-}"
    echo "    <li><a href=\"./pr-$PR_NUM/\">PR #$PR_NUM Preview →</a></li>"
  done

  # If there are no previews
  if ! compgen -G "pr-*" > /dev/null; then
    echo '    <li>No active PR previews</li>'
  fi

  echo '  </ul>'
  echo '</body>'
  echo '</html>'
} > index.html

# Commit only if there are changes
git add .
git commit -m "Remove preview for closed PR #$PR_NUMBER" || echo "ℹ️ Nothing to commit"
git push origin gh-pages-preview

echo "✅ Cleanup completed"