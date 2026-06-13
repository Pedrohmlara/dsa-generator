/**
 * GenerateButton — Submit button with loading state.
 *
 * Disabled when no topics are selected. Shows a spinner
 * and "Generating..." text during generation.
 */

/**
 * @param {HTMLElement} container - DOM element to mount into
 * @param {Function} onGenerate - Callback when clicked
 * @returns {{ setEnabled: (v: boolean) => void, setLoading: (v: boolean) => void, setCount: (n: number) => void }}
 */
export function GenerateButton(container, onGenerate) {
  let enabled = false;
  let loading = false;
  let count = 0;

  function render() {
    const disabled = !enabled || loading;
    container.innerHTML = `
      <div class="generate-section">
        <button
          class="generate-btn ${loading ? 'generate-btn--loading' : ''}"
          id="generate-btn"
          type="button"
          ${disabled ? 'disabled' : ''}
        >
          ${loading
            ? '<span class="generate-btn__spinner"></span> Generating...'
            : '▶ Generate Guide'
          }
        </button>
        <span class="generate-summary">
          ${count > 0
            ? `${count} topic${count !== 1 ? 's' : ''} selected`
            : 'Select at least one topic'
          }
        </span>
      </div>
    `;

    container.querySelector('#generate-btn')?.addEventListener('click', () => {
      if (!disabled) onGenerate();
    });
  }

  render();

  return {
    setEnabled(v) {
      enabled = v;
      render();
    },
    setLoading(v) {
      loading = v;
      render();
    },
    setCount(n) {
      count = n;
      enabled = n > 0;
      render();
    },
  };
}
