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
  document.body.addEventListener("htmx:beforeRequest", function (evt) {
    // Disable button during request
    convertBtn.disabled = true;
  });

  document.body.addEventListener("htmx:afterRequest", function (evt) {
    // Re-enable button after request
    convertBtn.disabled = false;

    if (evt.detail.successful) {
      showNotification("Conversion completed successfully!", "success");
    } else {
      showNotification("Conversion failed. Please try again.", "error");
    }
  });
});
