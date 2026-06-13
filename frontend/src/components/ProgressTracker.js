/**
 * ProgressTracker — Vertical stepper showing pipeline phases.
 *
 * Displays three phases (Planning, Writing, Coding) with
 * pending/active/complete states updated via SSE events.
 */

const PHASES = [
  { id: 'planning', icon: '📋', label: 'Planning curriculum...',  completeLabel: 'Curriculum planned' },
  { id: 'writing',  icon: '✍️', label: 'Writing content...',      completeLabel: 'Content generated' },
  { id: 'coding',   icon: '💻', label: 'Adding code examples...', completeLabel: 'Code examples ready' },
];

/**
 * @param {HTMLElement} container
 * @returns {{ show: () => void, hide: () => void, updatePhase: (phase: string, status: string, message?: string) => void, reset: () => void }}
 */
export function ProgressTracker(container) {
  const phaseStatus = {};
  const phaseMessage = {};
  let visible = false;

  function render() {
    if (!visible) {
      container.innerHTML = '';
      return;
    }

    container.innerHTML = `
      <div class="progress-tracker animate-fade-in">
        <div class="progress-steps">
          ${PHASES.map(p => {
            const status = phaseStatus[p.id] || 'pending';
            const message = phaseMessage[p.id];
            const cls = status === 'active' ? 'progress-step--active'
                      : status === 'complete' ? 'progress-step--complete'
                      : '';
            const icon = status === 'complete' ? '✓'
                       : status === 'active' ? p.icon
                       : '·';
            const label = status === 'complete' ? (message || p.completeLabel)
                        : status === 'active' ? (message || p.label)
                        : p.label;
            return `
              <div class="progress-step ${cls}">
                <span class="progress-step__icon">${icon}</span>
                <span>${label}</span>
              </div>
            `;
          }).join('')}
        </div>
      </div>
    `;
  }

  return {
    show() {
      visible = true;
      render();
    },

    hide() {
      visible = false;
      render();
    },

    updatePhase(phase, status, message) {
      phaseStatus[phase] = status;
      if (message) phaseMessage[phase] = message;
      render();
    },

    reset() {
      Object.keys(phaseStatus).forEach(k => delete phaseStatus[k]);
      Object.keys(phaseMessage).forEach(k => delete phaseMessage[k]);
      visible = false;
      render();
    },
  };
}
