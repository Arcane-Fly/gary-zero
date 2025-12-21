/**
 * Barrel exports for webui/js utilities
 * Provides centralized access to all JavaScript utility modules
 */

// Core utilities
export { default as api } from './api.js';
export { default as apiResponseHandler } from './api-response-handler.js';
export { default as formValidator } from './form-validator.js';
export { default as logger } from './logger.js';
export { default as domHelpers } from './dom-helpers.js';
export { default as timeUtils } from './time-utils.js';

// Alpine.js related
export { default as AlpineStore } from './AlpineStore.js';
export { default as alpineRegistration } from './alpine-registration.js';
export { default as alpineErrorRecovery } from './alpine-error-recovery.js';
export { default as cspAlpineFix } from './csp-alpine-fix.js';

// UI Components
export { default as components } from './components.js';
export { default as modals } from './modals.js';
export { default as modal } from './modal.js';
export { default as messages } from './messages.js';
export { default as enhancedUX } from './enhanced-ux.js';
export { default as sidebarTabs } from './sidebar-tabs.js';
export { default as imageModal } from './image_modal.js';

// Error handling
export { default as errorBoundary } from './error-boundary.js';
export { default as errorReporting } from './error-reporting.js';
export { default as unifiedErrorHandler } from './unified-error-handler.js';

// Logging
export { default as consoleLogger } from './console-logger.js';
export { default as unifiedLogger } from './unified-logger.js';

// Features
export { default as fileBrowser } from './file_browser.js';
export { default as history } from './history.js';
export { default as scheduler } from './scheduler.js';
export { default as settings } from './settings.js';
export { default as speech } from './speech.js';
export { default as speechBrowser } from './speech_browser.js';
export { default as tunnel } from './tunnel.js';

// Initialization
export { default as initFw } from './initFw.js';
export { default as initOrchestrator } from './init-orchestrator.js';
export { default as uiInit } from './ui-init.js';

// Utilities
export { default as sleep } from './sleep.js';
export { default as timeout } from './timeout.js';
export { default as activityMonitor } from './activity-monitor.js';
export { default as chatInputAutoresize } from './chat-input-autoresize.js';
export { default as shellIframe } from './shell-iframe.js';
export { default as aiActionVisualization } from './ai-action-visualization.js';
export { default as uiStructureRebuilder } from './ui-structure-rebuilder.js';
export { default as vscodeIntegration } from './vscode-integration.js';
export { default as verifyFixes } from './verify-fixes.js';
