from pathlib import Path

css_path = Path("src/style.css")
css = css_path.read_text(encoding="utf-8")
css += """

/*
 * Mobile sidebar: dock the navigation at the top.
 * The navigation owns the scroll area; decorative/account sections are
 * removed on small screens so they cannot push links below the viewport.
 */
@media (max-width: 900px) {
  .redesign-shell .sidebar {
    box-sizing: border-box;
    position: fixed !important;
    top: calc(58px + env(safe-area-inset-top, 0px)) !important;
    right: 0 !important;
    bottom: 0 !important;
    left: auto !important;
    width: min(290px, calc(100vw - 42px)) !important;
    min-width: 0 !important;
    height: auto !important;
    max-height: none !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: flex-start !important;
    align-items: stretch !important;
    gap: 0 !important;
    overflow: hidden !important;
    padding: 12px 14px calc(12px + env(safe-area-inset-bottom, 0px)) !important;
    overscroll-behavior: contain;
    background: var(--panel);
    transform: translateX(105%);
  }

  .redesign-shell.sidebar-open .sidebar {
    transform: translateX(0) !important;
  }

  .redesign-shell .sidebar > .brand {
    order: 0 !important;
    display: flex !important;
    flex: 0 0 auto !important;
    align-items: center;
    min-height: 42px;
    margin: 0 0 10px !important;
    padding: 3px 8px 10px !important;
  }

  .redesign-shell .sidebar .workspace-label {
    display: none !important;
  }

  .redesign-shell .sidebar > .side-nav {
    order: 1 !important;
    position: relative !important;
    inset: auto !important;
    display: flex !important;
    flex: 1 1 auto !important;
    flex-direction: column !important;
    justify-content: flex-start !important;
    align-items: stretch !important;
    gap: 5px !important;
    width: 100% !important;
    min-width: 0 !important;
    min-height: 0 !important;
    max-height: none !important;
    margin: 0 !important;
    padding: 0 2px 8px !important;
    overflow-x: hidden !important;
    overflow-y: auto !important;
    overscroll-behavior-y: contain;
    -webkit-overflow-scrolling: touch;
    touch-action: pan-y;
    scrollbar-width: thin;
  }

  .redesign-shell .sidebar .side-nav .nav-item {
    position: static !important;
    inset: auto !important;
    display: flex !important;
    flex: 0 0 auto !important;
    width: 100% !important;
    min-width: 0 !important;
    min-height: 46px !important;
    height: auto !important;
    margin: 0 !important;
    transform: none !important;
  }

  .redesign-shell .sidebar > .sidebar-bottom {
    display: none !important;
  }

  .redesign-shell.sidebar-open .sidebar-scrim {
    position: fixed !important;
    inset: calc(58px + env(safe-area-inset-top, 0px)) 0 0 !important;
    z-index: 65 !important;
    display: block !important;
  }
}

@media (max-width: 900px) and (max-height: 650px) {
  .redesign-shell .sidebar {
    padding-top: 8px !important;
  }

  .redesign-shell .sidebar > .brand {
    min-height: 36px;
    margin-bottom: 6px !important;
    padding-bottom: 6px !important;
  }

  .redesign-shell .sidebar > .side-nav {
    gap: 3px !important;
  }

  .redesign-shell .sidebar .side-nav .nav-item {
    min-height: 42px !important;
  }
}
"""
css_path.write_text(css, encoding="utf-8")
print("Applied top-docked mobile navigation with an independent scroll area.")
