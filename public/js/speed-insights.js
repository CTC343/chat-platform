// Vercel Speed Insights integration for vanilla JavaScript
// This script injects the Vercel Speed Insights tracking code

(function() {
  'use strict';
  
  // Initialize Speed Insights queue
  window.si = window.si || function () {
    (window.siq = window.siq || []).push(arguments);
  };
  
  // Inject the Speed Insights script
  var script = document.createElement('script');
  script.defer = true;
  script.src = '/_vercel/speed-insights/script.js';
  
  // Add error handling
  script.onerror = function() {
    console.warn('Vercel Speed Insights script failed to load. This is expected in local development.');
  };
  
  // Append to document
  if (document.head) {
    document.head.appendChild(script);
  } else {
    document.addEventListener('DOMContentLoaded', function() {
      document.head.appendChild(script);
    });
  }
})();
