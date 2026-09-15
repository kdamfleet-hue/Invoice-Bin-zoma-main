(function () {
  "use strict";

  function initSaasInteractions() {
    var html = document.getElementById("rootHtml");
    var langButton = document.getElementById("langBtn");
    var video = document.getElementById("clipVid");
    var modal = document.getElementById("clipModal");
    var closeButton = document.getElementById("clipClose");
    var clipTriggers = document.querySelectorAll("[data-km-clip-open]");

    if (!html) return;

    function applyLanguage(lang) {
      var english = lang === "en";
      html.lang = english ? "en" : "ar";
      html.dir = english ? "ltr" : "rtl";

      document.querySelectorAll("[data-ar]").forEach(function (element) {
        var value = english ? element.getAttribute("data-en") : element.getAttribute("data-ar");
        if (value !== null) element.textContent = value;
      });

      if (langButton) langButton.textContent = english ? "AR" : "EN";
      try { window.localStorage.setItem("km_lang", english ? "en" : "ar"); } catch (_) { /* storage may be blocked */ }
    }

    function openClip(event) {
      if (event) event.preventDefault();
      if (!modal) return;
      modal.classList.add("open");
      modal.setAttribute("aria-hidden", "false");
      if (video) {
        video.currentTime = 0;
        video.play().catch(function () {});
      }
    }

    function closeClip(event) {
      if (event) event.preventDefault();
      if (video) video.pause();
      if (modal) {
        modal.classList.remove("open");
        modal.setAttribute("aria-hidden", "true");
      }
    }

    var savedLanguage = "ar";
    try { savedLanguage = window.localStorage.getItem("km_lang") || "ar"; } catch (_) { /* use Arabic default */ }
    applyLanguage(savedLanguage);

    if (langButton) {
      langButton.addEventListener("click", function () {
        applyLanguage(html.lang === "ar" ? "en" : "ar");
      });
    }

    clipTriggers.forEach(function (trigger) {
      trigger.addEventListener("click", openClip);
    });

    if (closeButton) closeButton.addEventListener("click", closeClip);
    if (modal) {
      modal.addEventListener("click", function (event) {
        if (event.target === modal) closeClip(event);
      });
    }

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && modal && modal.classList.contains("open")) closeClip(event);
    });

    window.KM_openClip = openClip;
    window.KM_closeClip = closeClip;
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initSaasInteractions);
  } else {
    initSaasInteractions();
  }
}());
