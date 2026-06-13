/**
 * TopicSelector — Multi-select topic chips grouped by category.
 * 
 * Renders pill-shaped toggleable chips for each DSA topic,
 * organized into Data Structures and Algorithms categories.
 * Includes "Select All" and "Clear" quick actions.
 */

/**
 * @param {HTMLElement} container - DOM element to mount into
 * @param {Function} onChange - Callback(selectedTopics: string[])
 * @returns {{ getSelected: () => string[], setTopics: (data: object) => void }}
 */
export function TopicSelector(container, onChange) {
  let categories = [];
  const selected = new Set();

  function render() {
    container.innerHTML = `
      <div class="topic-selector">
        <div class="section-label">
          Select Topics
          <span class="section-label__count" id="topic-count">${selected.size} selected</span>
        </div>
        ${categories.map((cat, ci) => `
          <div class="topic-category animate-fade-in-up" style="animation-delay: ${ci * 80}ms">
            <div class="topic-category__name">${cat.name}</div>
            <div class="topic-grid">
              ${cat.topics.map(t => `
                <button
                  class="topic-chip ${selected.has(t.id) ? 'topic-chip--selected' : ''}"
                  data-topic="${t.id}"
                  id="topic-${t.id}"
                  type="button"
                  aria-pressed="${selected.has(t.id)}"
                >
                  <span class="topic-chip__check">${selected.has(t.id) ? '✓' : ''}</span>
                  ${t.label}
                </button>
              `).join('')}
            </div>
          </div>
        `).join('')}
        <div class="topic-actions">
          <button class="topic-action-btn" id="select-all-btn" type="button">Select All</button>
          <button class="topic-action-btn" id="clear-all-btn" type="button">Clear</button>
        </div>
      </div>
    `;

    // Bind click handlers.
    container.querySelectorAll('.topic-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        const id = chip.dataset.topic;
        if (selected.has(id)) {
          selected.delete(id);
        } else {
          selected.add(id);
        }
        render();
        onChange(Array.from(selected));
      });
    });

    container.querySelector('#select-all-btn')?.addEventListener('click', () => {
      categories.forEach(cat => cat.topics.forEach(t => selected.add(t.id)));
      render();
      onChange(Array.from(selected));
    });

    container.querySelector('#clear-all-btn')?.addEventListener('click', () => {
      selected.clear();
      render();
      onChange(Array.from(selected));
    });
  }

  return {
    getSelected: () => Array.from(selected),

    setTopics(data) {
      categories = data.categories || [];
      render();
    },
  };
}
