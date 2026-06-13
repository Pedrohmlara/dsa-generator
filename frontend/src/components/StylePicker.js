/**
 * StylePicker — Single-select learning style cards.
 *
 * Renders 4 cards with icon, name, and description.
 * Radio-button behavior: only one can be selected at a time.
 */

/**
 * @param {HTMLElement} container - DOM element to mount into
 * @param {Function} onChange - Callback(selectedStyle: string)
 * @returns {{ getSelected: () => string|null, setStyles: (styles: Array) => void }}
 */
export function StylePicker(container, onChange) {
  let styles = [];
  let selected = null;

  function render() {
    container.innerHTML = `
      <div class="style-picker">
        <div class="section-label">Choose Learning Style</div>
        <div class="style-grid">
          ${styles.map((s, i) => `
            <button
              class="style-card ${selected === s.id ? 'style-card--selected' : ''} animate-fade-in-up"
              data-style="${s.id}"
              id="style-${s.id}"
              type="button"
              aria-pressed="${selected === s.id}"
              style="animation-delay: ${i * 60}ms"
            >
              <div class="style-card__icon">${s.icon}</div>
              <div class="style-card__name">${s.label}</div>
              <div class="style-card__desc">${s.description}</div>
            </button>
          `).join('')}
        </div>
      </div>
    `;

    container.querySelectorAll('.style-card').forEach(card => {
      card.addEventListener('click', () => {
        selected = card.dataset.style;
        render();
        onChange(selected);
      });
    });
  }

  return {
    getSelected: () => selected,

    setStyles(data) {
      styles = data || [];
      // Default to first style.
      if (styles.length > 0 && !selected) {
        selected = styles[0].id;
        onChange(selected);
      }
      render();
    },
  };
}
