/**
 * DSA Learning Guide Generator — Main Application
 *
 * Wires together all components: TopicSelector, StylePicker,
 * GenerateButton, ProgressTracker, and GuideRenderer.
 * Manages the two application views: Setup and Guide.
 */

import './styles/index.css';
import './styles/components.css';
import './styles/guide.css';

import { TopicSelector } from './components/TopicSelector.js';
import { StylePicker } from './components/StylePicker.js';
import { GenerateButton } from './components/GenerateButton.js';
import { ProgressTracker } from './components/ProgressTracker.js';
import { GuideRenderer } from './components/GuideRenderer.js';
import { HistoryView } from './components/HistoryView.js';
import { fetchTopics, generateGuide } from './lib/api.js';

// ── State ──────────────────────────────────────────────────
let selectedTopics = [];
let selectedStyle = null;
let currentView = 'setup'; // 'setup' | 'guide' | 'history'
let abortController = null;

// ── DOM References ─────────────────────────────────────────
const app = document.getElementById('app');

// ── Render App Shell ───────────────────────────────────────
function renderShell() {
  app.innerHTML = `
    <header class="header">
      <div class="header__logo">
        <span class="header__logo-icon">⚡</span>
        DSA Guide Generator
        <span class="header__badge">AI-Powered</span>
      </div>
      <nav class="header__nav">
        <button id="nav-generator" class="toc__back" style="font-weight:600;">Generator</button>
        <button id="nav-history" class="toc__back">History</button>
      </nav>
    </header>
    <main class="main">
      <div id="setup-view" class="setup-view">
        <h1 class="setup-view__title">Build Your DSA Study Guide</h1>
        <p class="setup-view__subtitle">
          Select the topics you want to master and choose your learning style.
          Our AI will generate a comprehensive, personalized study guide.
        </p>
        <div id="topic-selector"></div>
        <div id="style-picker"></div>
        <div id="generate-button"></div>
      </div>
      <div id="progress-area"></div>
      <div id="guide-view" style="display: none;"></div>
      <div id="history-view-container" style="display: none;"></div>
    </main>
  `;
}

// ── Initialize ─────────────────────────────────────────────
async function init() {
  renderShell();

  const topicContainer = document.getElementById('topic-selector');
  const styleContainer = document.getElementById('style-picker');
  const generateContainer = document.getElementById('generate-button');
  const progressContainer = document.getElementById('progress-area');
  const guideContainer = document.getElementById('guide-view');
  const setupContainer = document.getElementById('setup-view');

  // Mount components
  const topicSelector = TopicSelector(topicContainer, (topics) => {
    selectedTopics = topics;
    generateBtn.setCount(topics.length);
  });

  const stylePicker = StylePicker(styleContainer, (style) => {
    selectedStyle = style;
  });

  const generateBtn = GenerateButton(generateContainer, () => {
    startGeneration();
  });

  const progressTracker = ProgressTracker(progressContainer);
  const guideRenderer = GuideRenderer(guideContainer);

  const historyContainer = document.getElementById('history-view-container');
  const historyView = HistoryView(historyContainer, (guide) => {
    // When a guide is selected from history
    currentView = 'guide';
    setupContainer.style.display = 'none';
    historyContainer.style.display = 'none';
    guideContainer.style.display = 'block';
    guideRenderer.init(() => {
      // Back goes to history instead of setup if we came from history
      showHistory();
    });
    guideRenderer.loadFullGuide(guide);
  });

  // Nav actions
  document.getElementById('nav-generator').addEventListener('click', () => {
    currentView = 'setup';
    setupContainer.style.display = 'block';
    guideContainer.style.display = 'none';
    historyContainer.style.display = 'none';
    progressTracker.reset();
    guideRenderer.clear();
  });

  document.getElementById('nav-history').addEventListener('click', showHistory);

  function showHistory() {
    currentView = 'history';
    setupContainer.style.display = 'none';
    guideContainer.style.display = 'none';
    historyView.show();
    if (abortController) {
      abortController.abort();
      abortController = null;
    }
  }

  // Fetch topics from backend
  try {
    const data = await fetchTopics();
    topicSelector.setTopics(data);
    stylePicker.setStyles(data.styles);
  } catch (err) {
    console.error('Failed to fetch topics:', err);
    // Fallback: use hardcoded data
    topicSelector.setTopics(getFallbackData());
    stylePicker.setStyles(getFallbackData().styles);
  }

  // ── Generation Flow ────────────────────────────────────
  function startGeneration() {
    // Switch to guide view
    currentView = 'guide';
    setupContainer.style.display = 'none';
    guideContainer.style.display = 'block';

    // Reset state
    guideRenderer.init(() => {
      // Back button handler goes to setup
      currentView = 'setup';
      setupContainer.style.display = 'block';
      guideContainer.style.display = 'none';
      historyContainer.style.display = 'none';
      progressTracker.reset();
      guideRenderer.clear();
      generateBtn.setLoading(false);
      if (abortController) {
        abortController.abort();
        abortController = null;
      }
    });

    progressTracker.show();
    generateBtn.setLoading(true);

    abortController = generateGuide(
      { topics: selectedTopics, style: selectedStyle },
      {
        onProgress(data) {
          progressTracker.updatePhase(data.phase, data.status, data.message);
        },

        onOutline(data) {
          // Could display outline preview — for now, just log
          console.log('Curriculum outline:', data);
        },

        onContent(token) {
          guideRenderer.append(token, 'content');
        },

        onCode(token) {
          guideRenderer.append(token, 'code');
        },

        onSectionStart(data) {
          console.log(`Section ${data.index}: ${data.title} (${data.type})`);
        },

        onSectionEnd(data) {
          console.log(`Section ${data.index} complete (${data.type})`);
        },

        onDone(data) {
          guideRenderer.finish();
          progressTracker.hide();
          generateBtn.setLoading(false);
          console.log('Generation complete:', data);
        },

        onError(data) {
          guideRenderer.finish();
          generateBtn.setLoading(false);
          showError(data.message || 'An error occurred during generation.');
        },
      }
    );
  }
}

// ── Error Toast ────────────────────────────────────────────
function showError(message) {
  // Remove existing
  document.querySelector('.error-toast')?.remove();

  const toast = document.createElement('div');
  toast.className = 'error-toast';
  toast.innerHTML = `
    <button class="error-toast__close" onclick="this.parentElement.remove()">×</button>
    ${message}
  `;
  document.body.appendChild(toast);

  setTimeout(() => toast.remove(), 8000);
}

// ── Fallback Data (when backend is unreachable) ────────────
function getFallbackData() {
  return {
    categories: [
      {
        name: 'Data Structures',
        topics: [
          { id: 'arrays', label: 'Arrays' },
          { id: 'strings', label: 'Strings' },
          { id: 'hash_tables', label: 'Hash Tables (Maps / Sets)' },
          { id: 'linked_lists', label: 'Linked Lists' },
          { id: 'stacks', label: 'Stacks' },
          { id: 'queues', label: 'Queues' },
          { id: 'trees', label: 'Trees (Binary Trees, BST)' },
          { id: 'heaps', label: 'Heaps (Priority Queues)' },
          { id: 'graphs', label: 'Graphs' },
          { id: 'tries', label: 'Tries' },
          { id: 'union_find', label: 'Disjoint Set (Union-Find)' },
        ],
      },
      {
        name: 'Algorithms & Techniques',
        topics: [
          { id: 'dfs', label: 'Depth-First Search (DFS)' },
          { id: 'bfs', label: 'Breadth-First Search (BFS)' },
          { id: 'binary_search', label: 'Binary Search' },
          { id: 'two_pointers', label: 'Two Pointers' },
          { id: 'sliding_window', label: 'Sliding Window' },
          { id: 'backtracking', label: 'Backtracking' },
          { id: 'dynamic_programming', label: 'Dynamic Programming' },
          { id: 'greedy', label: 'Greedy Algorithms' },
          { id: 'topological_sort', label: 'Topological Sort' },
          { id: 'prefix_sum', label: 'Prefix Sum' },
          { id: 'bit_manipulation', label: 'Bit Manipulation' },
          { id: 'divide_and_conquer', label: 'Divide and Conquer' },
        ],
      },
    ],
    styles: [
      { id: 'interview_prep', label: 'Interview Prep', icon: '🎯', description: 'Patterns, complexity analysis, and common interview variations' },
      { id: 'academic', label: 'Academic Deep-Dive', icon: '📚', description: 'Formal definitions, proofs, and mathematical analysis' },
      { id: 'visual', label: 'Visual / Intuitive', icon: '🧠', description: 'Step-by-step walkthroughs, diagrams, and analogies' },
      { id: 'speed_run', label: 'Speed Run', icon: '⚡', description: 'Concise cheat-sheet style, just the essentials' },
    ],
  };
}

// ── Boot ───────────────────────────────────────────────────
init();
