# BestClient browser redesign

Branch: `ui-redesign-browser-20261024`

The redesign stays native C++/DDNet UI. No HTML/WebView runtime is added.

## Implemented

- new muted ink / aubergine / dusty-rose / sage palette instead of default neon gaming colors;
- denser, flatter server-browser surfaces with low radii;
- custom selected-server row with a thin accent marker;
- calmer semantic ping colors;
- redesigned right toolbox tabs and active indicator;
- redesigned bottom status/command area;
- compact Refresh utility control;
- Connect is a native command control rather than a large green/gold CTA;
- existing server-browser behavior remains in place (filters, friends, BestClient panel, search/exclude/address, hotkeys, Enter/double-click connect).

## Build on Windows

Requirements: Git, Python 3, CMake, Visual Studio 2022 with Desktop development with C++, and Vulkan SDK when `-DVULKAN=ON` is used.

From the repository root run:

```bat
build-ui-redesign-win64.bat
```

The CMake configure step runs `scripts/apply_browser_redesign.py`. It validates every expected source fragment before editing `src/game/client/components/menus_browser.cpp`; if the upstream browser structure no longer matches, configuration fails instead of silently producing a partial redesign.

The build script runs `package_default` and copies produced ZIP packages into:

```text
dist-ui-redesign\
```

Use the packaged client as a complete build. If replacing an existing portable BestClient installation manually, replace the executable and `data` directory together rather than mixing data from different builds.
