// Wait for Tailwind CSS to be available
function initializeTailwindConfig() {
  if (typeof tailwind !== "undefined") {
    console.log("Tailwind is ready, initializing config...");
    tailwind.config = {
      theme: {
        extend: {
          animation: {
            "fade-in": "fadeIn 1s ease-in-out",
            "slide-up": "slideUp 0.8s ease-out",
            float: "float 3s ease-in-out infinite",
            "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
          },
          keyframes: {
            fadeIn: {
              "0%": { opacity: "0" },
              "100%": { opacity: "1" },
            },
            slideUp: {
              "0%": { opacity: "0", transform: "translateY(30px)" },
              "100%": { opacity: "1", transform: "translateY(0)" },
            },
            float: {
              "0%, 100%": { transform: "translateY(0px)" },
              "50%": { transform: "translateY(-10px)" },
            },
          },
          backgroundImage: {
            "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
            mesh: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
          },
        },
      },
    };
  } else {
    // Retry after a short delay if Tailwind isn't ready yet
    setTimeout(initializeTailwindConfig, 100);
  }
}

// Initialize when DOM is loaded
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initializeTailwindConfig);
} else {
  initializeTailwindConfig();
}
