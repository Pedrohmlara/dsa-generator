/**
 * GuideRenderer — Displays streamed Markdown content.
 *
 * Renders content and code sections with:
 * - Real-time markdown → HTML conversion
 * - Auto-updating Table of Contents sidebar
 * - Typing cursor while content streams
 * - Syntax highlighting via highlight.js (CDN)
 */

import { markdownToHtml, extractHeadings } from '../lib/markdown.js';

/**
 * @param {HTMLElement} container - DOM element to mount the guide view into
 * @returns {object} Controller with append, clear, etc.
 */
export function GuideRenderer(container) {
  let contentMarkdown = '';
  let codeMarkdown = '';
  let isStreaming = false;
  let currentType = 'content'; // 'content' or 'code'
  let tocContainer = null;
  let contentContainer = null;

  function renderShell() {
    container.innerHTML = `
      <div class="guide-view animate-fade-in">
        <aside class="guide-sidebar no-scrollbar">
          <button class="toc__back" id="guide-back-btn">← Back to selection</button>
          <button class="toc__back" id="guide-export-btn" style="margin-top: 8px;">📥 Export Markdown</button>
          <nav>
            <ul class="toc" id="guide-toc"></ul>
          </nav>
        </aside>
        <div class="guide-content no-scrollbar" id="guide-content">
          <div class="guide-markdown" id="guide-markdown"></div>
        </div>
      </div>
    `;
    tocContainer = container.querySelector('#guide-toc');
    contentContainer = container.querySelector('#guide-markdown');
  }

  function updateTOC() {
    if (!tocContainer) return;
    const allMd = contentMarkdown + '\n\n' + codeMarkdown;
    const headings = extractHeadings(allMd);
    tocContainer.innerHTML = headings.map(h => `
      <li class="toc__item">
        <a class="toc__link" href="#${h.id}" style="padding-left: ${(h.level - 2) * 16 + 12}px">
          ${h.text}
        </a>
      </li>
    `).join('');
  }

  function renderContent() {
    if (!contentContainer) return;

    const allMd = contentMarkdown + '\n\n' + codeMarkdown;
    let html = markdownToHtml(allMd);

    // Add typing cursor if still streaming
    if (isStreaming) {
      html += '<span class="typing-cursor"></span>';
    }

    contentContainer.innerHTML = html;

    // Try to highlight code blocks if highlight.js is loaded
    if (window.hljs) {
      contentContainer.querySelectorAll('pre code').forEach(block => {
        window.hljs.highlightElement(block);
      });
    }

    updateTOC();
  }

  /** Scroll to bottom smoothly while content streams */
  function scrollToBottom() {
    if (!contentContainer) return;
    const guideContent = contentContainer.closest('.guide-content');
    if (guideContent) {
      // Only auto-scroll if user is near the bottom
      const isNearBottom = window.innerHeight + window.scrollY >= document.body.scrollHeight - 200;
      if (isNearBottom) {
        window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
      }
    }
  }

  // Batch rendering: accumulate tokens and render periodically
  let renderTimer = null;
  function scheduleRender() {
    if (renderTimer) return;
    renderTimer = requestAnimationFrame(() => {
      renderTimer = null;
      renderContent();
      scrollToBottom();
    });
  }

  return {
    /**
     * Initialize the guide shell (call once when switching to guide view).
     * @param {Function} onBack - Callback when "Back" is clicked.
     */
    init(onBack) {
      renderShell();
      container.querySelector('#guide-back-btn')?.addEventListener('click', onBack);
      container.querySelector('#guide-export-btn')?.addEventListener('click', () => {
        const allMd = contentMarkdown + '\n\n' + codeMarkdown;
        const blob = new Blob([allMd], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `DSA_Guide_${new Date().toISOString().slice(0, 10)}.md`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      });
    },

    /**
     * Append a token to the current section type.
     * @param {string} token
     * @param {'content'|'code'} type
     */
    append(token, type = 'content') {
      if (type === 'code') {
        codeMarkdown += token;
      } else {
        contentMarkdown += token;
      }
      isStreaming = true;
      scheduleRender();
    },

    /** Mark streaming as complete. */
    finish() {
      isStreaming = false;
      renderContent();
    },

    /** Reset all content. */
    clear() {
      contentMarkdown = '';
      codeMarkdown = '';
      isStreaming = false;
      if (contentContainer) contentContainer.innerHTML = '';
      if (tocContainer) tocContainer.innerHTML = '';
    },

    /** Set the current section type for incoming tokens. */
    setType(type) {
      currentType = type;
    },

    /** Load a fully generated guide from history. */
    loadFullGuide(guide) {
      this.clear();
      isStreaming = false;
      if (!guide.outline || !guide.outline.sections) return;

      guide.outline.sections.forEach(sec => {
        if (sec.content) contentMarkdown += sec.content + '\n\n';
        if (sec.code) codeMarkdown += sec.code + '\n\n';
      });

      renderContent();
    }
  };
}
