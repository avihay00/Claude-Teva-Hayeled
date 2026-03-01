// =============================================================================
// main.js  —  Teva Hayeled Website Scripts
// =============================================================================
// Features:
//   • Sticky navbar shadow on scroll
//   • Mobile nav drawer (open / close / overlay click)
//   • Scroll-driven fade-in animations (IntersectionObserver)
//   • Back-to-top button
// =============================================================================

(function () {
  'use strict';

  // ─────────────────────────────────────────────────────────────────────────
  // Element references
  // ─────────────────────────────────────────────────────────────────────────
  const navbar     = document.getElementById('navbar');
  const navToggle  = document.getElementById('navToggle');
  const navClose   = document.getElementById('navClose');
  const navDrawer  = document.getElementById('navDrawer');
  const navOverlay = document.getElementById('navOverlay');
  const backToTop  = document.getElementById('backToTop');


  // ─────────────────────────────────────────────────────────────────────────
  // Navbar — add shadow when page is scrolled
  // ─────────────────────────────────────────────────────────────────────────
  function onScroll() {
    if (window.scrollY > 10) {
      navbar.style.boxShadow = '0 4px 20px rgba(44,74,30,0.25)';
    } else {
      navbar.style.boxShadow = '';
    }

    // Back-to-top visibility
    if (backToTop) {
      if (window.scrollY > 400) {
        backToTop.classList.add('is-visible');
      } else {
        backToTop.classList.remove('is-visible');
      }
    }
  }

  window.addEventListener('scroll', onScroll, { passive: true });


  // ─────────────────────────────────────────────────────────────────────────
  // Mobile nav drawer
  // ─────────────────────────────────────────────────────────────────────────
  function openDrawer() {
    navDrawer.classList.add('is-open');
    navOverlay.classList.add('is-visible');
    document.body.style.overflow = 'hidden';
  }

  function closeDrawer() {
    navDrawer.classList.remove('is-open');
    navOverlay.classList.remove('is-visible');
    document.body.style.overflow = '';
  }

  if (navToggle)  navToggle.addEventListener('click', openDrawer);
  if (navClose)   navClose.addEventListener('click', closeDrawer);
  if (navOverlay) navOverlay.addEventListener('click', closeDrawer);

  // Close drawer on Escape key
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeDrawer();
  });


  // ─────────────────────────────────────────────────────────────────────────
  // Scroll-driven fade-in  (uses IntersectionObserver)
  // ─────────────────────────────────────────────────────────────────────────
  if ('IntersectionObserver' in window) {
    const fadeEls = document.querySelectorAll('.fade-in');

    const observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-visible');
            observer.unobserve(entry.target); // animate once only
          }
        });
      },
      { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
    );

    fadeEls.forEach(function (el) {
      observer.observe(el);
    });
  } else {
    // Fallback — just show everything
    document.querySelectorAll('.fade-in').forEach(function (el) {
      el.classList.add('is-visible');
    });
  }


  // ─────────────────────────────────────────────────────────────────────────
  // Back to top button
  // ─────────────────────────────────────────────────────────────────────────
  if (backToTop) {
    backToTop.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }


  // ─────────────────────────────────────────────────────────────────────────
  // Auto-dismiss flash messages after 5 seconds
  // ─────────────────────────────────────────────────────────────────────────
  var flashes = document.querySelectorAll('.flash');
  flashes.forEach(function (flash) {
    setTimeout(function () {
      flash.style.opacity = '0';
      flash.style.transform = 'translateY(-8px)';
      flash.style.transition = 'opacity 0.4s, transform 0.4s';
      setTimeout(function () { flash.remove(); }, 400);
    }, 5000);
  });

})();
