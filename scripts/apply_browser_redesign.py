#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "src/game/client/components/menus_browser.cpp"
text = PATH.read_text(encoding="utf-8")

if "namespace BrowserVisual" in text:
    print("BestClient browser redesign already applied")
    raise SystemExit(0)


def replace_once(old: str, new: str, name: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{name}: expected exactly one match, got {count}")
    text = text.replace(old, new, 1)


replace_once(
'''static constexpr ColorRGBA HIGHLIGHTED_TEXT_COLOR = ColorRGBA(0.4f, 0.4f, 1.0f, 1.0f);''',
'''namespace BrowserVisual
{
static constexpr ColorRGBA Canvas = ColorRGBA(0.063f, 0.078f, 0.094f, 1.0f);
static constexpr ColorRGBA Surface = ColorRGBA(0.090f, 0.110f, 0.133f, 1.0f);
static constexpr ColorRGBA SurfaceRaised = ColorRGBA(0.129f, 0.118f, 0.157f, 1.0f);
static constexpr ColorRGBA SurfaceHover = ColorRGBA(0.165f, 0.157f, 0.196f, 1.0f);
static constexpr ColorRGBA RowSelected = ColorRGBA(0.251f, 0.200f, 0.247f, 1.0f);
static constexpr ColorRGBA Control = ColorRGBA(0.106f, 0.125f, 0.149f, 1.0f);
static constexpr ColorRGBA ControlHover = ColorRGBA(0.153f, 0.173f, 0.204f, 1.0f);
static constexpr ColorRGBA ControlPressed = ColorRGBA(0.071f, 0.086f, 0.106f, 1.0f);
static constexpr ColorRGBA Border = ColorRGBA(0.294f, 0.275f, 0.314f, 1.0f);
static constexpr ColorRGBA Accent = ColorRGBA(0.753f, 0.553f, 0.651f, 1.0f);
static constexpr ColorRGBA AccentSoft = ColorRGBA(0.651f, 0.604f, 0.753f, 1.0f);
static constexpr ColorRGBA Secondary = ColorRGBA(0.471f, 0.678f, 0.639f, 1.0f);
static constexpr ColorRGBA Warm = ColorRGBA(0.835f, 0.702f, 0.416f, 1.0f);
static constexpr ColorRGBA TextMuted = ColorRGBA(0.667f, 0.643f, 0.655f, 1.0f);
static constexpr ColorRGBA Success = ColorRGBA(0.494f, 0.741f, 0.533f, 1.0f);
static constexpr ColorRGBA Warning = ColorRGBA(0.820f, 0.667f, 0.408f, 1.0f);
static constexpr ColorRGBA Danger = ColorRGBA(0.843f, 0.478f, 0.482f, 1.0f);
}

static constexpr ColorRGBA HIGHLIGHTED_TEXT_COLOR = BrowserVisual::Accent;''',
"palette")

replace_once(
'''\tstatic const ColorRGBA COLORS[] = {ColorRGBA(0.5f, 1.0f, 0.5f), ColorRGBA(0.4f, 0.4f, 1.0f), ColorRGBA(0.75f, 0.75f, 0.75f)};
\tstatic const ColorRGBA COLORS_AFK[] = {ColorRGBA(1.0f, 1.0f, 0.5f), ColorRGBA(0.4f, 0.75f, 1.0f), ColorRGBA(0.6f, 0.6f, 0.6f)};''',
'''\tstatic const ColorRGBA COLORS[] = {BrowserVisual::AccentSoft, BrowserVisual::Secondary, BrowserVisual::TextMuted};
\tstatic const ColorRGBA COLORS_AFK[] = {BrowserVisual::Warm, BrowserVisual::Secondary, BrowserVisual::TextMuted};''',
"player colors")

replace_once(
'''\treturn (Afk ? COLORS_AFK[i] : COLORS[i]).WithAlpha(0.3f + (Inside ? 0.15f : 0.0f) + (InSelectedServer ? 0.12f : 0.0f));''',
'''\treturn (Afk ? COLORS_AFK[i] : COLORS[i]).WithAlpha(0.16f + (Inside ? 0.08f : 0.0f) + (InSelectedServer ? 0.10f : 0.0f));''',
"player alpha")

replace_once(
'''\treturn color_cast<ColorRGBA>(ColorHSLA((300.0f - std::clamp(Latency, 0, 300)) / 1000.0f, 1.0f, 0.5f));''',
'''\tif(Latency <= 55)
\t\treturn BrowserVisual::Success;
\tif(Latency <= 110)
\t\treturn BrowserVisual::Warning;
\treturn BrowserVisual::Danger;''',
"ping colors")

replace_once(
'''\tHeaders.Draw(ColorRGBA(1.0f, 1.0f, 1.0f, 0.25f), IGraphics::CORNER_T, 5.0f);
\tHeaders.VSplitRight(s_ListBox.ScrollbarWidthMax(), &Headers, nullptr);
\tView.Draw(ColorRGBA(0.0f, 0.0f, 0.0f, 0.15f), IGraphics::CORNER_NONE, 0.0f);''',
'''\tHeaders.Draw(BrowserVisual::SurfaceRaised.WithAlpha(0.94f), IGraphics::CORNER_T, 4.0f);
\tHeaders.VSplitRight(s_ListBox.ScrollbarWidthMax(), &Headers, nullptr);
\tView.Draw(BrowserVisual::Canvas.WithAlpha(0.80f), IGraphics::CORNER_NONE, 0.0f);''',
"server list surfaces")

replace_once(
'''\t\t\tBestClientRenderIndicatorIcon(Graphics(), Icon, false, false, ColorRGBA(1.0f, 1.0f, 1.0f, 0.9f));''',
'''\t\t\tBestClientRenderIndicatorIcon(Graphics(), Icon, false, false, BrowserVisual::AccentSoft.WithAlpha(0.95f));''',
"bestclient header icon")

replace_once(
'''\t\t\tTextRender()->SetRenderFlags(ETextRenderFlags::TEXT_RENDER_FLAG_ONLY_ADVANCE_WIDTH | ETextRenderFlags::TEXT_RENDER_FLAG_NO_X_BEARING | ETextRenderFlags::TEXT_RENDER_FLAG_NO_Y_BEARING | ETextRenderFlags::TEXT_RENDER_FLAG_NO_PIXEL_ALIGNMENT | ETextRenderFlags::TEXT_RENDER_FLAG_NO_OVERSIZE);
\t\t\tUi()->DoLabel(&Col.m_Rect, FontIcon::STAR, 14.0f, TEXTALIGN_MC);
\t\t\tTextRender()->SetRenderFlags(0);''',
'''\t\t\tTextRender()->SetRenderFlags(ETextRenderFlags::TEXT_RENDER_FLAG_ONLY_ADVANCE_WIDTH | ETextRenderFlags::TEXT_RENDER_FLAG_NO_X_BEARING | ETextRenderFlags::TEXT_RENDER_FLAG_NO_Y_BEARING | ETextRenderFlags::TEXT_RENDER_FLAG_NO_PIXEL_ALIGNMENT | ETextRenderFlags::TEXT_RENDER_FLAG_NO_OVERSIZE);
\t\t\tTextRender()->TextColor(BrowserVisual::Warm);
\t\t\tUi()->DoLabel(&Col.m_Rect, FontIcon::STAR, 14.0f, TEXTALIGN_MC);
\t\t\tTextRender()->TextColor(TextRender()->DefaultTextColor());
\t\t\tTextRender()->SetRenderFlags(0);''',
"favorite header")

replace_once(
'''\t\tconst bool ShowPreview = PreviewRow && PreviewHeight > 0.5f;
\t\tif(ShowPreview && AddressSelected)
\t\t\ts_ListBox.SuppressNextSelectionHighlight();''',
'''\t\tconst bool ShowPreview = PreviewRow && PreviewHeight > 0.5f;
\t\tif(AddressSelected)
\t\t\ts_ListBox.SuppressNextSelectionHighlight();''',
"selection suppression")

replace_once(
'''\t\tconst ColorRGBA PreviewFrame(1.0f, 1.0f, 1.0f, s_ListBox.Active() ? 0.5f : 0.33f);''',
'''\t\tconst ColorRGBA PreviewFrame = BrowserVisual::AccentSoft.WithAlpha(s_ListBox.Active() ? 0.55f : 0.34f);''',
"preview frame")

replace_once(
'''\t\tif(!ListItem.m_Visible)
\t\t{
\t\t\t// reset active item, if not visible
\t\t\tif(Ui()->CheckActiveItem(pItem))
\t\t\t\tUi()->SetActiveItem(nullptr);

\t\t\t// don't render invisible items
\t\t\t// bestclient
\t\t\tif(ShowPreview)
\t\t\t\tm_ServerMapPreview.Render(PreviewRect, PreviewFrame);
\t\t\t// bestclient
\t\t\tcontinue;
\t\t}

\t\tconst float FontSize = 12.0f;''',
'''\t\tif(!ListItem.m_Visible)
\t\t{
\t\t\t// reset active item, if not visible
\t\t\tif(Ui()->CheckActiveItem(pItem))
\t\t\t\tUi()->SetActiveItem(nullptr);

\t\t\t// don't render invisible items
\t\t\t// bestclient
\t\t\tif(ShowPreview)
\t\t\t\tm_ServerMapPreview.Render(PreviewRect, PreviewFrame);
\t\t\t// bestclient
\t\t\tcontinue;
\t\t}

\t\tif(AddressSelected && !ShowPreview)
\t\t{
\t\t\tCUIRect Selected = ListItem.m_Rect;
\t\t\tSelected.Draw(BrowserVisual::RowSelected.WithAlpha(s_ListBox.Active() ? 0.92f : 0.66f), IGraphics::CORNER_ALL, 3.0f);
\t\t\tCUIRect Marker;
\t\t\tSelected.VSplitLeft(2.0f, &Marker, nullptr);
\t\t\tMarker.Draw(BrowserVisual::Accent, IGraphics::CORNER_L, 2.0f);
\t\t}

\t\tconst float FontSize = 12.0f;''',
"selected row")

replace_once(
'''RenderBrowserIcons(*pUiElement->Rect(UI_ELEM_LOCK_ICON), &Button, ColorRGBA(0.75f, 0.75f, 0.75f, 1.0f), TextRender()->DefaultTextOutlineColor(), FontIcon::LOCK, TEXTALIGN_MC);''',
'''RenderBrowserIcons(*pUiElement->Rect(UI_ELEM_LOCK_ICON), &Button, BrowserVisual::TextMuted, TextRender()->DefaultTextOutlineColor(), FontIcon::LOCK, TEXTALIGN_MC);''',
"lock icon")

replace_once(
'''RenderBrowserIcons(*pUiElement->Rect(UI_ELEM_KEY_ICON), &Button, ColorRGBA(0.75f, 0.75f, 0.75f, 1.0f), TextRender()->DefaultTextOutlineColor(), FontIcon::KEY, TEXTALIGN_MC);''',
'''RenderBrowserIcons(*pUiElement->Rect(UI_ELEM_KEY_ICON), &Button, BrowserVisual::TextMuted, TextRender()->DefaultTextOutlineColor(), FontIcon::KEY, TEXTALIGN_MC);''',
"login icon")

replace_once(
'''RenderBrowserIcons(*pUiElement->Rect(UI_ELEM_FAVORITE_ICON), &Button, ColorRGBA(1.0f, 0.85f, 0.3f, 1.0f), TextRender()->DefaultTextOutlineColor(), FontIcon::STAR, TEXTALIGN_MC);''',
'''RenderBrowserIcons(*pUiElement->Rect(UI_ELEM_FAVORITE_ICON), &Button, BrowserVisual::Warm, TextRender()->DefaultTextOutlineColor(), FontIcon::STAR, TEXTALIGN_MC);''',
"favorite row icon")

replace_once(
'''void CMenus::RenderServerbrowserStatusBox(CUIRect StatusBox, bool WasListboxItemActivated)
{
\t// Render bar that shows the loading progression.''',
'''void CMenus::RenderServerbrowserStatusBox(CUIRect StatusBox, bool WasListboxItemActivated)
{
\tStatusBox.Draw(BrowserVisual::Surface.WithAlpha(0.94f), IGraphics::CORNER_ALL, 5.0f);

\t// Render bar that shows the loading progression.''',
"status surface")

replace_once(
'''\t\tRefreshBar.Draw(ColorRGBA(1.0f, 1.0f, 1.0f, RefreshBarAlpha), IGraphics::CORNER_NONE, 0.0f);
\t}

\tTextRender()->SetFontPreset(EFontPreset::ICON_FONT);''',
'''\t\tRefreshBar.Draw(BrowserVisual::AccentSoft.WithAlpha(RefreshBarAlpha), IGraphics::CORNER_NONE, 0.0f);
\t}

\tStatusBox.Margin(4.0f, &StatusBox);

\tTextRender()->SetFontPreset(EFontPreset::ICON_FONT);''',
"status progress")

replace_once(
'''\tStatusBox.VSplitRight(135.0f, &SearchInfoAndAddr, &ServersAndConnect);
\tif(SearchInfoAndAddr.w > 350.0f)
\t\tSearchInfoAndAddr.VSplitLeft(350.0f, &SearchInfoAndAddr, nullptr);
\tSearchInfoAndAddr.HSplitTop(40.0f, &SearchAndInfo, &ServerAddr);
\tServersAndConnect.HSplitTop(35.0f, &ServersPlayersOnline, &ConnectButtons);
\tConnectButtons.HSplitTop(5.0f, nullptr, &ConnectButtons);''',
'''\tStatusBox.VSplitRight(230.0f, &SearchInfoAndAddr, &ServersAndConnect);
\tSearchInfoAndAddr.VSplitRight(8.0f, &SearchInfoAndAddr, nullptr);
\tSearchInfoAndAddr.HSplitTop(40.0f, &SearchAndInfo, &ServerAddr);
\tServersAndConnect.HSplitTop(26.0f, &ServersPlayersOnline, &ConnectButtons);
\tConnectButtons.HSplitTop(3.0f, nullptr, &ConnectButtons);''',
"status layout")

old_buttons = '''\t// buttons
\t{
\t\tCUIRect ButtonRefresh, ButtonConnect;
\t\tConnectButtons.VSplitMid(&ButtonRefresh, &ButtonConnect, 5.0f);

\t\t// refresh button
\t\t{
\t\t\tchar aLabelBuf[32] = {0};
\t\t\tconst auto &&RefreshLabelFunc = [this, aLabelBuf]() mutable {
\t\t\t\tif(ServerBrowser()->IsRefreshing() || ServerBrowser()->IsGettingServerlist())
\t\t\t\t\tstr_format(aLabelBuf, sizeof(aLabelBuf), "%s%s", FontIcon::ARROW_ROTATE_RIGHT, FontIcon::ELLIPSIS);
\t\t\t\telse
\t\t\t\t\tstr_copy(aLabelBuf, FontIcon::ARROW_ROTATE_RIGHT);
\t\t\t\treturn aLabelBuf;
\t\t\t};

\t\t\tSMenuButtonProperties Props;
\t\t\tProps.m_HintRequiresStringCheck = true;
\t\t\tProps.m_UseIconFont = true;

\t\t\tstatic CButtonContainer s_RefreshButton;
\t\t\tif(Ui()->DoButton_Menu(m_RefreshButton, &s_RefreshButton, RefreshLabelFunc, &ButtonRefresh, Props) || (!Ui()->IsPopupOpen() && (Input()->KeyPress(KEY_F5) || (Input()->KeyPress(KEY_R) && Input()->ModifierIsPressed()))))
\t\t\t{
\t\t\t\tRefreshBrowserTab(true);
\t\t\t}
\t\t}

\t\t// connect button
\t\t{
\t\t\tconst auto &&ConnectLabelFunc = []() { return FontIcon::RIGHT_TO_BRACKET; };

\t\t\tSMenuButtonProperties Props;
\t\t\tProps.m_UseIconFont = true;
\t\t\tProps.m_Color = ColorRGBA(0.5f, 1.0f, 0.5f, 0.5f);

\t\t\tstatic CButtonContainer s_ConnectButton;
\t\t\tif(Ui()->DoButton_Menu(m_ConnectButton, &s_ConnectButton, ConnectLabelFunc, &ButtonConnect, Props) || WasListboxItemActivated || (!Ui()->IsPopupOpen() && Ui()->ConsumeHotkey(CUi::HOTKEY_ENTER)))
\t\t\t{
\t\t\t\tConnect(g_Config.m_UiServerAddress);
\t\t\t}
\t\t}
\t}
}'''

new_buttons = '''\t// bottom command controls
\t{
\t\tCUIRect ButtonRefresh, ButtonConnect;
\t\tConnectButtons.VSplitLeft(42.0f, &ButtonRefresh, &ButtonConnect);
\t\tButtonConnect.VSplitLeft(6.0f, nullptr, &ButtonConnect);

\t\t// refresh: compact utility control, deliberately quieter than Connect
\t\t{
\t\t\tchar aLabelBuf[32] = {0};
\t\t\tif(ServerBrowser()->IsRefreshing() || ServerBrowser()->IsGettingServerlist())
\t\t\t\tstr_format(aLabelBuf, sizeof(aLabelBuf), "%s%s", FontIcon::ARROW_ROTATE_RIGHT, FontIcon::ELLIPSIS);
\t\t\telse
\t\t\t\tstr_copy(aLabelBuf, FontIcon::ARROW_ROTATE_RIGHT);

\t\t\tstatic CButtonContainer s_RefreshButton;
\t\t\tconst int Click = Ui()->DoButtonLogic(&s_RefreshButton, 0, &ButtonRefresh, BUTTONFLAG_LEFT);
\t\t\tconst bool Hot = Ui()->HotItem() == &s_RefreshButton;
\t\t\tconst bool Active = Ui()->CheckActiveItem(&s_RefreshButton);
\t\t\tButtonRefresh.Draw(BrowserVisual::Border.WithAlpha(Hot ? 0.85f : 0.55f), IGraphics::CORNER_ALL, 4.0f);
\t\t\tCUIRect Inner = ButtonRefresh;
\t\t\tInner.Margin(1.0f, &Inner);
\t\t\tInner.Draw(Active ? BrowserVisual::ControlPressed : (Hot ? BrowserVisual::ControlHover : BrowserVisual::Control), IGraphics::CORNER_ALL, 3.0f);

\t\t\tTextRender()->SetFontPreset(EFontPreset::ICON_FONT);
\t\t\tTextRender()->SetRenderFlags(ETextRenderFlags::TEXT_RENDER_FLAG_ONLY_ADVANCE_WIDTH | ETextRenderFlags::TEXT_RENDER_FLAG_NO_X_BEARING | ETextRenderFlags::TEXT_RENDER_FLAG_NO_Y_BEARING | ETextRenderFlags::TEXT_RENDER_FLAG_NO_PIXEL_ALIGNMENT | ETextRenderFlags::TEXT_RENDER_FLAG_NO_OVERSIZE);
\t\t\tTextRender()->TextColor(Hot ? BrowserVisual::AccentSoft : BrowserVisual::TextMuted);
\t\t\tUi()->DoLabel(&Inner, aLabelBuf, 14.0f, TEXTALIGN_MC);
\t\t\tTextRender()->TextColor(TextRender()->DefaultTextColor());
\t\t\tTextRender()->SetRenderFlags(0);
\t\t\tTextRender()->SetFontPreset(EFontPreset::DEFAULT_FONT);

\t\t\tif(Click || (!Ui()->IsPopupOpen() && (Input()->KeyPress(KEY_F5) || (Input()->KeyPress(KEY_R) && Input()->ModifierIsPressed())))
\t\t\t\tRefreshBrowserTab(true);
\t\t}

\t\t// connect: command control, not a bright launcher-style CTA
\t\t{
\t\t\tstatic CButtonContainer s_ConnectButton;
\t\t\tconst int Click = Ui()->DoButtonLogic(&s_ConnectButton, 0, &ButtonConnect, BUTTONFLAG_LEFT);
\t\t\tconst bool Hot = Ui()->HotItem() == &s_ConnectButton;
\t\t\tconst bool Active = Ui()->CheckActiveItem(&s_ConnectButton);

\t\t\tButtonConnect.Draw(BrowserVisual::Accent.WithAlpha(Hot ? 0.92f : 0.58f), IGraphics::CORNER_ALL, 4.0f);
\t\t\tCUIRect Inner = ButtonConnect;
\t\t\tInner.Margin(1.0f, &Inner);
\t\t\tif(Active)
\t\t\t\tInner.y += 1.0f;
\t\t\tInner.Draw(Active ? BrowserVisual::ControlPressed : (Hot ? BrowserVisual::SurfaceHover : BrowserVisual::SurfaceRaised), IGraphics::CORNER_ALL, 3.0f);

\t\t\tCUIRect Icon, Label;
\t\t\tInner.VSplitLeft(30.0f, &Icon, &Label);
\t\t\tLabel.VSplitLeft(4.0f, nullptr, &Label);
\t\t\tLabel.VSplitRight(10.0f, &Label, nullptr);

\t\t\tTextRender()->SetFontPreset(EFontPreset::ICON_FONT);
\t\t\tTextRender()->SetRenderFlags(ETextRenderFlags::TEXT_RENDER_FLAG_ONLY_ADVANCE_WIDTH | ETextRenderFlags::TEXT_RENDER_FLAG_NO_X_BEARING | ETextRenderFlags::TEXT_RENDER_FLAG_NO_Y_BEARING | ETextRenderFlags::TEXT_RENDER_FLAG_NO_PIXEL_ALIGNMENT | ETextRenderFlags::TEXT_RENDER_FLAG_NO_OVERSIZE);
\t\t\tTextRender()->TextColor(Hot ? BrowserVisual::Accent : BrowserVisual::AccentSoft);
\t\t\tUi()->DoLabel(&Icon, FontIcon::RIGHT_TO_BRACKET, 13.0f, TEXTALIGN_MC);
\t\t\tTextRender()->TextColor(TextRender()->DefaultTextColor());
\t\t\tTextRender()->SetRenderFlags(0);
\t\t\tTextRender()->SetFontPreset(EFontPreset::DEFAULT_FONT);
\t\t\tUi()->DoLabel(&Label, Localize("Connect"), 13.0f, TEXTALIGN_MC);

\t\t\tif(Click || WasListboxItemActivated || (!Ui()->IsPopupOpen() && Ui()->ConsumeHotkey(CUi::HOTKEY_ENTER)))
\t\t\t\tConnect(g_Config.m_UiServerAddress);
\t\t}
\t}
}'''
replace_once(old_buttons, new_buttons, "command controls")

replace_once(
'''\tconst ColorRGBA ColorActive = ColorRGBA(0.0f, 0.0f, 0.0f, 0.3f);
\tconst ColorRGBA ColorInactive = ColorRGBA(0.0f, 0.0f, 0.0f, 0.15f);

\tif(!Ui()->IsPopupOpen() && Ui()->ConsumeHotkey(CUi::HOTKEY_TAB))''',
'''\tconst ColorRGBA ColorActive = BrowserVisual::SurfaceRaised.WithAlpha(0.95f);
\tconst ColorRGBA ColorInactive = BrowserVisual::Canvas.WithAlpha(0.62f);

\tif(!Ui()->IsPopupOpen() && Ui()->ConsumeHotkey(CUi::HOTKEY_TAB))''',
"toolbox tabs")

replace_once(
'''\tRenderCenteredBestClientTabIcon(Graphics(), BestClientTabButton, ColorRGBA(1.0f, 1.0f, 1.0f, 0.95f));''',
'''\tRenderCenteredBestClientTabIcon(Graphics(), BestClientTabButton, g_Config.m_UiToolboxPage == UI_TOOLBOX_PAGE_BESTCLIENT ? BrowserVisual::AccentSoft : BrowserVisual::TextMuted);''',
"bestclient active tab")

replace_once(
'''\tTextRender()->SetRenderFlags(0);
\tTextRender()->SetFontPreset(EFontPreset::DEFAULT_FONT);
}

void CMenus::RenderServerbrowserToolBox(CUIRect ToolBox)
{
\tToolBox.Draw(ColorRGBA(0.0f, 0.0f, 0.0f, 0.3f), IGraphics::CORNER_B, 4.0f);''',
'''\tTextRender()->SetRenderFlags(0);
\tTextRender()->SetFontPreset(EFontPreset::DEFAULT_FONT);

\tCUIRect ActiveLine;
\tswitch(g_Config.m_UiToolboxPage)
\t{
\tcase UI_TOOLBOX_PAGE_FILTERS: ActiveLine = FilterTabButton; break;
\tcase UI_TOOLBOX_PAGE_INFO: ActiveLine = InfoTabButton; break;
\tcase UI_TOOLBOX_PAGE_BESTCLIENT: ActiveLine = BestClientTabButton; break;
\tcase UI_TOOLBOX_PAGE_FRIENDS: ActiveLine = FriendsTabButton; break;
\tdefault: ActiveLine = FilterTabButton; break;
\t}
\tActiveLine.HSplitBottom(2.0f, nullptr, &ActiveLine);
\tActiveLine.VMargin(8.0f, &ActiveLine);
\tActiveLine.Draw(BrowserVisual::Accent, IGraphics::CORNER_ALL, 1.0f);
}

void CMenus::RenderServerbrowserToolBox(CUIRect ToolBox)
{
\tToolBox.Draw(BrowserVisual::Surface.WithAlpha(0.92f), IGraphics::CORNER_B, 4.0f);''',
"tab marker and toolbox surface")

replace_once(
'''\tMainView.Draw(ms_ColorTabbarActive, IGraphics::CORNER_B, 10.0f);
\tMainView.Margin(10.0f, &MainView);
\tMainView.VSplitRight(205.0f, &ServerList, &ToolBox);
\tServerList.VSplitRight(5.0f, &ServerList, nullptr);''',
'''\tMainView.Draw(BrowserVisual::Canvas.WithAlpha(0.90f), IGraphics::CORNER_B, 7.0f);
\tMainView.Margin(8.0f, &MainView);
\tMainView.VSplitRight(220.0f, &ServerList, &ToolBox);
\tServerList.VSplitRight(6.0f, &ServerList, nullptr);''',
"browser shell")

replace_once(
'''\tServerList.HSplitBottom(65.0f, &ServerList, &StatusBox);''',
'''\tServerList.HSplitBottom(66.0f, &ServerList, &StatusBox);''',
"status height")

PATH.write_text(text, encoding="utf-8")
print(f"Applied native BestClient browser redesign to {PATH}")
