/**
 * Eko Browser Extension - Content Script
 *
 * This script runs on every page and can interact with the DOM
 */

console.log("Eko Content Script loaded");

// Listen for messages from background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "getPageContent") {
    // Extract page content
    sendResponse({
      title: document.title,
      url: window.location.href,
      html: document.documentElement.outerHTML,
    });
  }

  if (request.action === "executeScript") {
    // Execute custom script on the page
    try {
      // Execute the provided script
      const result = eval(request.script);
      sendResponse({ success: true, result });
    } catch (error: any) {
      sendResponse({ success: false, error: error.message });
    }
  }

  return true; // Keep channel open for async response
});

// Export empty object to make this a module
export {};
