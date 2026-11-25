from pathlib import Path

css_path = Path("src/style.css")
css = css_path.read_text(encoding="utf-8")
css += """

/* Mobile drawer: keep every navigation item reachable on short screens. */
@media (max-width: 900px) {
  .redesign-shell .sidebar {
    box-sizing: border-box;
    position: fixed !important;
    top: calc(58px + env(safe-area-inset-top, 0px));
    right: 0;
    bottom: 0;
    left: auto;
    width: min(290px, calc(100vw - 42px));
    min-width: 0;
    height: auto;
    max-height: calc(100vh - 58px - env(safe-area-inset-top, 0px));
    max-height: calc(100dvh - 58px - env(safe-area-inset-top, 0px));
    display: flex !important;
    flex-direction: column;
    align-items: stretch;
    overflow-x: hidden !important;
    overflow-y: auto !important;
    overscroll-behavior-y: contain;
    -webkit-overflow-scrolling: touch;
    touch-action: pan-y;
    padding: 16px 14px calc(20px + env(safe-area-inset-bottom, 0px));
  }

  .redesign-shell .sidebar > * {
    flex-shrink: 0;
    min-width: 0;
  }

  .redesign-shell .sidebar .brand {
    min-height: 44px;
    padding: 3px 8px 14px;
  }

  .redesign-shell .sidebar .workspace-label {
    margin: 6px 9px 9px;
  }

  .redesign-shell .sidebar .side-nav {
    display: flex;
    flex: 0 0 auto;
    flex-direction: column;
    gap: 5px;
    min-height: max-content;
    overflow: visible;
    padding-bottom: 4px;
  }

  .redesign-shell .sidebar .side-nav .nav-item {
    box-sizing: border-box;
    flex: 0 0 auto;
    min-height: 46px;
    height: auto;
    width: 100%;
  }

  .redesign-shell .sidebar .sidebar-bottom {
    flex: 0 0 auto;
    margin-top: 14px;
    padding-top: 10px;
  }

  .redesign-shell .sidebar .sidebar-help {
    padding: 12px;
  }

  .redesign-shell.sidebar-open .sidebar-scrim {
    position: fixed;
    inset: calc(58px + env(safe-area-inset-top, 0px)) 0 0;
    z-index: 65;
    display: block;
  }
}

@media (max-width: 900px) and (max-height: 650px) {
  .redesign-shell .sidebar {
    padding-top: 10px;
    padding-bottom: calc(12px + env(safe-area-inset-bottom, 0px));
  }

  .redesign-shell .sidebar .brand {
    padding-bottom: 8px;
  }

  .redesign-shell .sidebar .side-nav {
    gap: 3px;
  }

  .redesign-shell .sidebar .side-nav .nav-item {
    min-height: 42px;
  }

  .redesign-shell .sidebar .sidebar-bottom {
    margin-top: 8px;
    padding-top: 7px;
  }

  .redesign-shell .sidebar .sidebar-help p {
    line-height: 1.6;
  }

  .redesign-shell .sidebar .user-mini {
    margin-top: 9px;
    padding-top: 8px;
  }
}
"""
css_path.write_text(css, encoding="utf-8")
print("Applied mobile drawer scroll and viewport sizing fix.")
