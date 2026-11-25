from pathlib import Path

css_path = Path("src/style.css")
css = css_path.read_text(encoding="utf-8")
css += """

/* Definitive mobile drawer layout: pin navigation to the drawer's top edge. */
@media (max-width: 900px) {
  .redesign-shell .sidebar {
    position: fixed !important;
    top: calc(58px + env(safe-area-inset-top, 0px)) !important;
    right: 0 !important;
    bottom: 0 !important;
    left: auto !important;
    width: min(300px, calc(100vw - 36px)) !important;
    min-width: 0 !important;
    height: auto !important;
    max-height: none !important;
    box-sizing: border-box !important;
    display: block !important;
    overflow: hidden !important;
    padding: 12px 14px calc(12px + env(safe-area-inset-bottom, 0px)) !important;
    z-index: 90 !important;
    background: var(--panel) !important;
    transform: translateX(105%);
    transition: transform .22s ease !important;
    box-shadow: -18px 0 45px rgba(0,0,0,.18);
  }

  .redesign-shell.sidebar-open .sidebar {
    transform: translateX(0) !important;
  }

  /* Keep the brand as a compact header; the links are independently docked. */
  .redesign-shell .sidebar > .brand {
    position: absolute !important;
    top: 12px !important;
    right: 14px !important;
    left: 14px !important;
    height: 44px !important;
    min-height: 44px !important;
    margin: 0 !important;
    padding: 2px 8px 10px !important;
    display: flex !important;
    align-items: center !important;
    z-index: 2;
  }

  .redesign-shell .sidebar .workspace-label,
  .redesign-shell .sidebar > .sidebar-bottom {
    display: none !important;
  }

  /* Absolute positioning removes the flex/grid flow that kept pushing links down. */
  .redesign-shell .sidebar .side-nav {
    position: absolute !important;
    top: 68px !important;
    right: 14px !important;
    bottom: calc(12px + env(safe-area-inset-bottom, 0px)) !important;
    left: 14px !important;
    inset-inline: 14px !important;
    width: auto !important;
    height: auto !important;
    min-height: 0 !important;
    max-height: none !important;
    margin: 0 !important;
    padding: 8px 2px 14px !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: flex-start !important;
    align-items: stretch !important;
    gap: 7px !important;
    overflow-x: hidden !important;
    overflow-y: auto !important;
    overscroll-behavior: contain;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: thin;
    touch-action: pan-y;
  }

  .redesign-shell .sidebar .side-nav .nav-item {
    position: relative !important;
    inset: auto !important;
    flex: 0 0 auto !important;
    display: flex !important;
    width: 100% !important;
    min-width: 0 !important;
    min-height: 48px !important;
    height: 48px !important;
    margin: 0 !important;
    padding-inline: 13px !important;
    transform: none !important;
    border-radius: 12px !important;
  }

  .redesign-shell .mobile-appbar {
    position: fixed !important;
    z-index: 100 !important;
    top: 0 !important;
    right: 0 !important;
    left: 0 !important;
    width: 100% !important;
    height: calc(58px + env(safe-area-inset-top, 0px)) !important;
    padding-top: env(safe-area-inset-top, 0px) !important;
  }

  .redesign-shell .mobile-menu-toggle {
    position: relative;
    z-index: 101;
    width: 42px !important;
    height: 42px !important;
    min-width: 42px;
    display: grid !important;
    place-items: center;
    border-radius: 12px !important;
    touch-action: manipulation;
  }

  .redesign-shell .sidebar-scrim,
  .redesign-shell.sidebar-open .sidebar-scrim {
    position: fixed !important;
    top: calc(58px + env(safe-area-inset-top, 0px)) !important;
    right: 0 !important;
    bottom: 0 !important;
    left: 0 !important;
    z-index: 85 !important;
    display: block !important;
    border: 0 !important;
    background: rgba(8, 10, 18, .52) !important;
    opacity: 0;
    visibility: hidden;
    pointer-events: none;
    transition: opacity .2s ease, visibility .2s ease;
  }

  .redesign-shell.sidebar-open .sidebar-scrim {
    opacity: 1;
    visibility: visible;
    pointer-events: auto;
  }
}

@media (max-width: 900px) and (max-height: 560px) {
  .redesign-shell .sidebar .side-nav { gap: 4px !important; padding-top: 3px !important; }
  .redesign-shell .sidebar .side-nav .nav-item { min-height: 42px !important; height: 42px !important; }
}

/* Small usability improvements across the platform. */
.redesign-shell button,
.public-site button,
.redesign-shell a,
.public-site a {
  -webkit-tap-highlight-color: transparent;
}

.redesign-shell button:focus-visible,
.public-site button:focus-visible,
.redesign-shell a:focus-visible,
.public-site a:focus-visible,
.redesign-shell input:focus-visible,
.public-site input:focus-visible,
.redesign-shell textarea:focus-visible,
.public-site textarea:focus-visible,
.redesign-shell select:focus-visible,
.public-site select:focus-visible {
  outline: 3px solid rgba(157, 125, 255, .7) !important;
  outline-offset: 3px !important;
}

.redesign-shell .button,
.public-site .button {
  min-height: 42px;
  border-radius: 11px;
  transition: transform .16s ease, box-shadow .16s ease, background .16s ease;
}

.redesign-shell .button:active,
.public-site .button:active {
  transform: scale(.98);
}

.redesign-shell input,
.redesign-shell textarea,
.redesign-shell select,
.public-site input,
.public-site textarea,
.public-site select {
  min-height: 42px;
  border-radius: 10px;
}

.redesign-shell .exam-card,
.public-site .public-panel,
.redesign-shell .dashboard-next-card {
  transition: border-color .18s ease, box-shadow .18s ease, transform .18s ease;
}

.redesign-shell .exam-card:hover,
.public-site .public-panel:hover {
  border-color: rgba(157, 125, 255, .32);
  box-shadow: 0 10px 28px rgba(0, 0, 0, .08);
}

@media (prefers-reduced-motion: reduce) {
  .redesign-shell *,
  .public-site * {
    scroll-behavior: auto !important;
    transition-duration: .01ms !important;
    animation-duration: .01ms !important;
    animation-iteration-count: 1 !important;
  }
}
"""
css_path.write_text(css, encoding="utf-8")
print("Applied absolutely top-docked mobile navigation and usability refinements.")
