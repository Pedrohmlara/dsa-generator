/**
 * Minimal Markdown → HTML converter.
 *
 * Handles the subset of Markdown that the agents produce:
 * headings, bold, italic, inline code, code blocks, lists,
 * blockquotes, tables, horizontal rules, and links.
 *
 * No external dependencies — just regex transforms.
 */

/**
 * Convert a Markdown string to HTML.
 * @param {string} md - Markdown source
 * @returns {string} HTML string
 */
export function markdownToHtml(md) {
  if (!md) return '';

  let html = md;

  // Fenced code blocks: ```lang\n...\n```
  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) => {
    const escaped = escapeHtml(code.trimEnd());
    const langBadge = lang ? `<span class="code-lang-badge">${lang}</span>` : '';
    return `<div class="code-block-wrapper">${langBadge}<button class="code-copy-btn" onclick="copyCode(this)">Copy</button><pre><code class="language-${lang || 'text'}">${escaped}</code></pre></div>`;
  });

  // Tables (support optional leading/trailing spaces and wrap in responsive container)
  html = html.replace(/^[ \t]*\|(.+)\|[ \t]*\n[ \t]*\|([-| :]+)\|[ \t]*\n((?:^[ \t]*\|.+\|[ \t]*(?:\n|$))*)/gm, (_, header, sep, body) => {
    const ths = header.split('|').filter(c => c.trim()).map(c => `<th>${c.trim()}</th>`).join('');
    const rows = body.trim().split('\n').filter(r => r.trim()).map(row => {
      const tds = row.split('|').filter(c => c.trim()).map(c => `<td>${c.trim()}</td>`).join('');
      return `<tr>${tds}</tr>`;
    }).join('');
    return `<div class="table-responsive"><table><thead><tr>${ths}</tr></thead><tbody>${rows}</tbody></table></div>`;
  });

  // Blockquotes
  html = html.replace(/^> (.+)$/gm, '<blockquote><p>$1</p></blockquote>');
  // Merge consecutive blockquotes
  html = html.replace(/<\/blockquote>\n<blockquote>/g, '\n');

  // Headings
  html = html.replace(/^#### (.+)$/gm, '<h4>$1</h4>');
  html = html.replace(/^### (.+)$/gm, '<h3 id="__HEADING__">$1</h3>');
  html = html.replace(/^## (.+)$/gm, '<h2 id="__HEADING__">$1</h2>');
  html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');

  // Generate heading IDs
  html = html.replace(/__HEADING__/g, () => '');
  html = html.replace(/<(h[23]) id="">(.*?)<\/\1>/g, (_, tag, text) => {
    const id = text.toLowerCase().replace(/[^\w\s-]/g, '').replace(/\s+/g, '-').slice(0, 60);
    return `<${tag} id="${id}">${text}</${tag}>`;
  });

  // Horizontal rules
  html = html.replace(/^---$/gm, '<hr>');

  // Unordered lists
  html = html.replace(/^(\s*)[-*] (.+)$/gm, '$1<li>$2</li>');
  // Ordered lists
  html = html.replace(/^(\s*)\d+\. (.+)$/gm, '$1<li>$2</li>');
  // Wrap consecutive <li> in <ul>
  html = html.replace(/((?:<li>.*<\/li>\n?)+)/g, '<ul>$1</ul>');

  // Bold + Italic
  html = html.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>');
  // Bold
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  // Italic
  html = html.replace(/(?<!\*)\*([^*]+?)\*(?!\*)/g, '<em>$1</em>');

  // Inline code (but not inside code blocks)
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

  // Links
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');

  // Paragraphs: wrap lines that aren't already wrapped in block elements
  const blockTags = /^<(h[1-6]|ul|ol|li|table|thead|tbody|tr|th|td|pre|div|blockquote|hr)/;
  html = html
    .split('\n\n')
    .map(block => {
      block = block.trim();
      if (!block) return '';
      if (blockTags.test(block)) return block;
      return `<p>${block.replace(/\n/g, '<br>')}</p>`;
    })
    .join('\n');

  return html;
}

/**
 * Escape HTML special characters.
 * @param {string} str
 * @returns {string}
 */
function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/**
 * Extract heading info from Markdown for TOC generation.
 * @param {string} md
 * @returns {Array<{level: number, text: string, id: string}>}
 */
export function extractHeadings(md) {
  const headings = [];
  const regex = /^(#{2,3}) (.+)$/gm;
  let match;
  while ((match = regex.exec(md)) !== null) {
    const level = match[1].length;
    const text = match[2];
    const id = text.toLowerCase().replace(/[^\w\s-]/g, '').replace(/\s+/g, '-').slice(0, 60);
    headings.push({ level, text, id });
  }
  return headings;
}

// Expose copyCode globally for the onclick handler in code blocks.
if (typeof window !== 'undefined') {
  window.copyCode = function(btn) {
    const wrapper = btn.closest('.code-block-wrapper');
    const code = wrapper?.querySelector('code')?.textContent || '';
    navigator.clipboard.writeText(code).then(() => {
      btn.textContent = 'Copied!';
      btn.classList.add('code-copy-btn--copied');
      setTimeout(() => {
        btn.textContent = 'Copy';
        btn.classList.remove('code-copy-btn--copied');
      }, 2000);
    });
  };
}
