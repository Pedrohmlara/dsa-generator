import { getGuides, getGuide } from '../lib/api.js';

export function HistoryView(container, onSelectGuide) {
  let isVisible = false;

  const render = () => {
    container.innerHTML = `
      <div class="history-view">
        <h2 class="history-view__title">Your Study Guides</h2>
        <div class="history-view__content" id="history-content">
          <div class="history-view__loading animate-pulse">Loading past guides...</div>
        </div>
      </div>
    `;
  };

  const loadGuides = async () => {
    const content = document.getElementById('history-content');
    if (!content) return;

    try {
      const guides = await getGuides();
      
      if (guides.length === 0) {
        content.innerHTML = `<div class="history-view__empty">No guides generated yet.</div>`;
        return;
      }

      content.innerHTML = `
        <div class="history-list">
          ${guides.map(g => `
            <div class="history-card" data-id="${g.id}">
              <div class="history-card__header">
                <span class="history-card__date">${new Date(g.created_at).toLocaleDateString()}</span>
                <span class="history-card__style">${g.request.style}</span>
              </div>
              <div class="history-card__topics">
                ${g.request.topics.join(', ')}
              </div>
              <div class="history-card__meta">
                ${g.sections_count} sections
              </div>
            </div>
          `).join('')}
        </div>
      `;

      // Add click listeners
      content.querySelectorAll('.history-card').forEach(card => {
        card.addEventListener('click', async () => {
          const id = card.dataset.id;
          const originalText = card.innerHTML;
          card.innerHTML = `<div class="history-card__loading">Loading...</div>`;
          
          try {
            const guide = await getGuide(id);
            onSelectGuide(guide);
          } catch (e) {
            console.error(e);
            card.innerHTML = originalText;
            alert("Failed to load guide.");
          }
        });
      });

    } catch (e) {
      content.innerHTML = `<div class="history-view__error">Failed to load history.</div>`;
    }
  };

  // Initial render
  render();

  return {
    show: () => {
      isVisible = true;
      container.style.display = 'block';
      loadGuides();
    },
    hide: () => {
      isVisible = false;
      container.style.display = 'none';
    }
  };
}
