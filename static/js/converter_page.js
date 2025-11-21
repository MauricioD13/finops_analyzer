document.addEventListener("DOMContentLoaded", function () {
  const fileUpload = document.getElementById("file-upload");
  const dropZone = document.getElementById("drop-zone");
  const fileInfo = document.getElementById("file-info");
  const fileName = document.getElementById("file-name");
  const removeFileBtn = document.getElementById("remove-file");
  const convertBtn = document.getElementById("convert-btn");
  const selectProviderDetection = document.getElementById("provider_detection");
  const selectProviderGroup = document.getElementById("provider-group");
  selectProviderGroup.hidden = true;
  // File upload handling
  fileUpload.addEventListener("change", handleFileSelect);
  removeFileBtn.addEventListener("click", handleFileRemove);

  // Drag and drop handling
  dropZone.addEventListener("dragover", handleDragOver);
  dropZone.addEventListener("dragleave", handleDragLeave);
  dropZone.addEventListener("drop", handleFileDrop);
  selectProviderDetection.addEventListener("change", handleProviderDetection);

  function handleProviderDetection(e) {
    const provider_detection = selectProviderDetection.value;
    if (provider_detection === "manual") {
      selectProviderGroup.hidden = false;
    } else {
      selectProviderGroup.hidden = true;
    }
  }

  function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
      displayFileInfo(file);
    }
  }

  function handleDragOver(e) {
    e.preventDefault();
    dropZone.classList.add("border-cyan-400/70", "bg-white/10");
  }

  function handleDragLeave(e) {
    e.preventDefault();
    dropZone.classList.remove("border-cyan-400/70", "bg-white/10");
  }

  function handleFileDrop(e) {
    e.preventDefault();
    dropZone.classList.remove("border-cyan-400/70", "bg-white/10");

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      fileUpload.files = files;
      displayFileInfo(files[0]);
    }
  }

  function displayFileInfo(file) {
    fileName.textContent = file.name;
    fileInfo.classList.remove("hidden");
    convertBtn.disabled = false;
  }

  function handleFileRemove() {
    // Clear the file input
    fileUpload.value = "";

    // Hide file info
    fileInfo.classList.add("hidden");
    fileName.textContent = "";

    // Disable convert button
    convertBtn.disabled = true;

    // Show notification
    showNotification("File removed successfully", "info");
  }

  // Animate elements on scroll
  const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px",
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = "1";
        entry.target.style.transform = "translateY(0)";
      }
    });
  }, observerOptions);

  // Observe all animated elements
  document.querySelectorAll(".animate-slide-up").forEach((el) => {
    if (!el.style.animationDelay) {
      el.style.opacity = "0";
      el.style.transform = "translateY(30px)";
      el.style.transition = "all 0.8s ease-out";
      observer.observe(el);
    }
  });

  // Notification system
  function showNotification(message, type = "info") {
    const notification = document.createElement("div");
    notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg transition-all duration-300 transform translate-x-full ${
      type === "success"
        ? "bg-green-500/90 text-white"
        : type === "error"
        ? "bg-red-500/90 text-white"
        : "bg-blue-500/90 text-white"
    }`;
    notification.textContent = message;

    document.body.appendChild(notification);

    // Animate in
    setTimeout(() => {
      notification.classList.remove("translate-x-full");
    }, 100);

    // Remove after 3 seconds
    setTimeout(() => {
      notification.classList.add("translate-x-full");
      setTimeout(() => {
        document.body.removeChild(notification);
      }, 300);
    }, 3000);
  }

  // HTMX event listeners
  document.body.addEventListener('htmx:afterSwap', function(event) {
    // After HTMX swaps content, attach download button handler if it exists
    const downloadBtn = document.getElementById('download-btn');
    if (downloadBtn) {
      downloadBtn.addEventListener('click', handleDownload);
      showNotification("Conversion completed successfully!", "success");
    }
  });

  // Form submission handler - just for UI feedback
  document.getElementById("converter-form").addEventListener("submit", function () {
    // Disable convert button during submission
    convertBtn.disabled = true;
    // HTMX will handle the rest automatically
  });

  // Re-enable button after request completes
  document.body.addEventListener('htmx:afterRequest', function(event) {
    if (event.detail.successful) {
      // Keep button disabled after success
      // User can refresh page to convert another file
    } else {
      // Re-enable on error
      convertBtn.disabled = false;
      showNotification("Conversion failed. Please try again.", "error");
    }
  });

  // Function to handle file download
  async function handleDownload(e) {
    const downloadBtn = e.currentTarget;
    const fileName = downloadBtn.dataset.filename;

    // Disable button and show loading state
    downloadBtn.disabled = true;
    const originalContent = downloadBtn.innerHTML;
    downloadBtn.innerHTML = `
      <svg class="animate-spin w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      Downloading...
    `;

    try {
      const response = await fetch(`/download/${fileName}`);

      if (!response.ok) {
        throw new Error('Download failed');
      }

      // Get the blob from response
      const blob = await response.blob();

      // Create a temporary URL for the blob
      const url = window.URL.createObjectURL(blob);

      // Create a temporary anchor element and trigger download
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();

      // Clean up
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      showNotification("File downloaded successfully!", "success");

      // Update button with success state
      downloadBtn.innerHTML = `
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M5 13l4 4L19 7"></path>
        </svg>
        Downloaded!
      `;

    } catch (error) {
      showNotification("Download failed. Please try again.", "error");

      // Re-enable button and restore original content
      downloadBtn.disabled = false;
      downloadBtn.innerHTML = originalContent;
    }
  }
});
