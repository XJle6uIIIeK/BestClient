#include "outlines.h"

#include <engine/graphics.h>
#include <engine/shared/config.h>

#include <game/client/animstate.h>
#include <game/client/gameclient.h>
#include <game/client/render.h>
#include <game/mapitems.h>

// The order of this is the order of priority for outlines
enum
{
	OUTLINE_NONE = 0,
	OUTLINE_UNFREEZE,
	OUTLINE_FREEZE,
	OUTLINE_TELE,
	OUTLINE_KILL,
	OUTLINE_SOLID,
};

void COutlines::ClearRoundedCache()
{
	for(auto &[Key, Container] : m_RoundedContainers)
		Graphics()->DeleteQuadContainer(Container.first);
	m_RoundedContainers.clear();
}

void COutlines::OnShutdown()
{
	ClearRoundedCache();
}

void COutlines::OnMapLoad()
{
	ClearRoundedCache();
	m_Regions.Load(Layers());
	m_MapDataSize = ivec2(m_Regions.m_Width, m_Regions.m_Height);
	m_pMapData = m_Regions.m_vTypes.empty() ? nullptr : m_Regions.m_vTypes.data();
}

void COutlines::OnRender()
{
	if(!m_pMapData)
		return;
	if(GameClient()->m_MapLayersBackground.m_OnlineOnly && Client()->State() != IClient::STATE_ONLINE && Client()->State() != IClient::STATE_DEMOPLAYBACK)
		return;
	if(!g_Config.m_ClOverlayEntities && g_Config.m_TcOutlineEntities)
		return;
	if(!g_Config.m_TcOutline)
		return;

	const float Scale = 32.0f;

	float ScreenX0, ScreenY0, ScreenX1, ScreenY1;
	Graphics()->GetScreen(&ScreenX0, &ScreenY0, &ScreenX1, &ScreenY1);
	const float PixelsPerUnit = Graphics()->ScreenWidth() / std::max(1.0f, ScreenX1 - ScreenX0);

	// Cull tile outlines outside optimizer FPS fog (same area as other non-map draws)
	if(GameClient()->OptimizerFpsFogEnabled())
	{
		float HalfW = 0.0f;
		float HalfH = 0.0f;
		GameClient()->OptimizerFpsFogHalfExtents(HalfW, HalfH);
		if(HalfW > 0.0f && HalfH > 0.0f)
		{
			const vec2 Center = GameClient()->m_Camera.m_Center;
			ScreenX0 = std::max(ScreenX0, Center.x - HalfW);
			ScreenX1 = std::min(ScreenX1, Center.x + HalfW);
			ScreenY0 = std::max(ScreenY0, Center.y - HalfH);
			ScreenY1 = std::min(ScreenY1, Center.y + HalfH);
			if(ScreenX0 >= ScreenX1 || ScreenY0 >= ScreenY1)
				return;
		}
	}

	int StartY = (int)(ScreenY0 / Scale) - 1;
	int StartX = (int)(ScreenX0 / Scale) - 1;
	int EndY = (int)(ScreenY1 / Scale) + 1;
	int EndX = (int)(ScreenX1 / Scale) + 1;
	int MaxScale = 12;
	if(g_Config.m_BcEntitiesRounding == 0 && (EndX - StartX > Graphics()->ScreenWidth() / MaxScale || EndY - StartY > Graphics()->ScreenHeight() / MaxScale))
	{
		int EdgeX = (EndX - StartX) - (Graphics()->ScreenWidth() / MaxScale);
		StartX += EdgeX / 2;
		EndX -= EdgeX / 2;
		int EdgeY = (EndY - StartY) - (Graphics()->ScreenHeight() / MaxScale);
		StartY += EdgeY / 2;
		EndY -= EdgeY / 2;
	}

	auto GetTile = [&](int x, int y) {
		x = std::clamp(x, 0, m_MapDataSize.x - 1);
		y = std::clamp(y, 0, m_MapDataSize.y - 1);
		return m_pMapData[y * m_MapDataSize.x + x];
	};

	const bool Rounded = g_Config.m_BcEntitiesRounding > 0;
	const int Steps = RoundedTiles::Detail(g_Config.m_BcEntitiesRounding * 0.16f, PixelsPerUnit);
	if(m_RoundingPercent != g_Config.m_BcEntitiesRounding || m_RoundingMode != g_Config.m_BcEntitiesRoundingMode || m_RoundingSteps != Steps)
	{
		ClearRoundedCache();
		m_RoundingPercent = g_Config.m_BcEntitiesRounding;
		m_RoundingMode = g_Config.m_BcEntitiesRoundingMode;
		m_RoundingSteps = Steps;
	}
	Graphics()->TextureClear();
	Graphics()->BlendNormal();
	Graphics()->QuadsSetRotation(0);
	if(!Rounded)
		Graphics()->QuadsBegin();

	for(int y = StartY; y < EndY; y++)
	{
		for(int x = StartX; x < EndX; x++)
		{
			const int Type = GetTile(x, y);
			// Switch tiles cover earlier entity layers but have no configurable
			// outline. They still block their neighbors' rounded contours.
			if(Type == OUTLINE_NONE || Type == CEntityRegions::SWITCH)
				continue;
			class COutlineConfig
			{
			public:
				const int &m_Enable;
				const int &m_Width;
				const unsigned int &m_Color;
			};
			const COutlineConfig Config = [&]() -> COutlineConfig {
				if(Type == OUTLINE_SOLID)
					return {g_Config.m_TcOutlineSolid, g_Config.m_TcOutlineWidthSolid, g_Config.m_TcOutlineColorSolid};
				if(Type == OUTLINE_FREEZE)
					return {g_Config.m_TcOutlineFreeze, g_Config.m_TcOutlineWidthFreeze, g_Config.m_TcOutlineColorFreeze};
				if(Type == OUTLINE_UNFREEZE)
					return {g_Config.m_TcOutlineUnfreeze, g_Config.m_TcOutlineWidthUnfreeze, g_Config.m_TcOutlineColorUnfreeze};
				if(Type == OUTLINE_KILL)
					return {g_Config.m_TcOutlineKill, g_Config.m_TcOutlineWidthKill, g_Config.m_TcOutlineColorKill};
				if(Type == OUTLINE_TELE)
					return {g_Config.m_TcOutlineTele, g_Config.m_TcOutlineWidthTele, g_Config.m_TcOutlineColorTele};
				dbg_assert(false, "Invalid value for Type at %d, %d/%d, %d", x, y, m_MapDataSize.x, m_MapDataSize.y);
			}();
			if(!Config.m_Enable || Config.m_Width <= 0)
				continue;
			if(Rounded)
			{
				// Build the exact same shape as the visible tiles. The old priority
				// only selects the color of an edge shared by two categories.
				const unsigned Mask = m_Regions.Mask(x, y, Type);
				const unsigned Blockers = m_Regions.BlockerMask(x, y, Type);
				const unsigned Transition = m_Regions.TransitionCorners(x, y);
				const unsigned HigherMask = m_Regions.PriorityMask(x, y, Type) & ~Mask;
				if(Mask == 255)
					continue;
				const uint64_t Key = uint64_t(Mask) | (uint64_t(Blockers) << 8) | (uint64_t(HigherMask) << 16) | (uint64_t(Config.m_Width) << 24) | (uint64_t(Transition) << 40);
				auto It = m_RoundedContainers.find(Key);
				if(It == m_RoundedContainers.end())
				{
					auto Shape = RoundedTiles::Build(Mask, m_RoundingPercent * 0.16f, m_RoundingMode, m_RoundingSteps, Blockers, Transition);
					RoundedTiles::RemoveLowerPriorityEdges(Shape, HigherMask);
					const auto Triangles = RoundedTiles::Outline(Shape, Config.m_Width);
					std::vector<IGraphics::CFreeformItem> vItems;
					vItems.reserve(Triangles.size());
					for(const auto &T : Triangles)
						vItems.emplace_back(T[0], T[1], T[2], T[2]);
					Graphics()->SetColor(1, 1, 1, 1);
					const int Container = Graphics()->CreateQuadContainer(false);
					if(!vItems.empty())
						Graphics()->QuadContainerAddQuads(Container, vItems.data(), vItems.size());
					Graphics()->QuadContainerUpload(Container);
					It = m_RoundedContainers.emplace(Key, std::make_pair(Container, (int)vItems.size())).first;
				}
				Graphics()->SetColor(color_cast<ColorRGBA>(ColorHSLA(Config.m_Color, true)));
				for(int Offset = 0; Offset < It->second.second; Offset += 1024)
					Graphics()->RenderQuadContainerEx(It->second.first, Offset, std::min(1024, It->second.second - Offset), x * Scale, y * Scale);
				continue;
			}
			// Find neighbours
			const bool aNeighbors[8] = {
				GetTile(x - 1, y - 1) >= Type,
				GetTile(x - 0, y - 1) >= Type,
				GetTile(x + 1, y - 1) >= Type,
				GetTile(x - 1, y + 0) >= Type,
				GetTile(x + 1, y + 0) >= Type,
				GetTile(x - 1, y + 1) >= Type,
				GetTile(x + 0, y + 1) >= Type,
				GetTile(x + 1, y + 1) >= Type,
			};
			// Figure out edges
			IGraphics::CQuadItem aQuads[8];
			int NumQuads = 0;
			// Lone corners first
			if(!aNeighbors[0] && aNeighbors[1] && aNeighbors[3])
				aQuads[NumQuads++] = IGraphics::CQuadItem(x * Scale, y * Scale, Config.m_Width, Config.m_Width);
			if(!aNeighbors[2] && aNeighbors[1] && aNeighbors[4])
				aQuads[NumQuads++] = IGraphics::CQuadItem(x * Scale + Scale - Config.m_Width, y * Scale, Config.m_Width, Config.m_Width);
			if(!aNeighbors[5] && aNeighbors[3] && aNeighbors[6])
				aQuads[NumQuads++] = IGraphics::CQuadItem(x * Scale, y * Scale + Scale - Config.m_Width, Config.m_Width, Config.m_Width);
			if(!aNeighbors[7] && aNeighbors[6] && aNeighbors[4])
				aQuads[NumQuads++] = IGraphics::CQuadItem(x * Scale + Scale - Config.m_Width, y * Scale + Scale - Config.m_Width, Config.m_Width, Config.m_Width);
			// Top
			if(!aNeighbors[1])
				aQuads[NumQuads++] = IGraphics::CQuadItem(x * Scale, y * Scale, Scale, Config.m_Width);
			// Bottom
			if(!aNeighbors[6])
				aQuads[NumQuads++] = IGraphics::CQuadItem(x * Scale, y * Scale + Scale - Config.m_Width, Scale, Config.m_Width);
			// Left
			if(!aNeighbors[3])
			{
				if(aNeighbors[1] && aNeighbors[6])
					aQuads[NumQuads++] = IGraphics::CQuadItem(x * Scale, y * Scale, Config.m_Width, Scale);
				else if(aNeighbors[6])
					aQuads[NumQuads++] = IGraphics::CQuadItem(x * Scale, y * Scale + Config.m_Width, Config.m_Width, Scale - Config.m_Width);
				else if(aNeighbors[1])
					aQuads[NumQuads++] = IGraphics::CQuadItem(x * Scale, y * Scale, Config.m_Width, Scale - Config.m_Width);
				else
					aQuads[NumQuads++] = IGraphics::CQuadItem(x * Scale, y * Scale + Config.m_Width, Config.m_Width, Scale - Config.m_Width * 2.0f);
			}
			// Right
			if(!aNeighbors[4])
			{
				if(aNeighbors[1] && aNeighbors[6])
					aQuads[NumQuads++] = IGraphics::CQuadItem(x * Scale + Scale - Config.m_Width, y * Scale, Config.m_Width, Scale);
				else if(aNeighbors[6])
					aQuads[NumQuads++] = IGraphics::CQuadItem(x * Scale + Scale - Config.m_Width, y * Scale + Config.m_Width, Config.m_Width, Scale - Config.m_Width);
				else if(aNeighbors[1])
					aQuads[NumQuads++] = IGraphics::CQuadItem(x * Scale + Scale - Config.m_Width, y * Scale, Config.m_Width, Scale - Config.m_Width);
				else
					aQuads[NumQuads++] = IGraphics::CQuadItem(x * Scale + Scale - Config.m_Width, y * Scale + Config.m_Width, Config.m_Width, Scale - Config.m_Width * 2.0f);
			}
			if(NumQuads <= 0)
				continue;
			Graphics()->SetColor(color_cast<ColorRGBA>(ColorHSLA(Config.m_Color, true)));
			Graphics()->QuadsDrawTL(aQuads, NumQuads);
		}
	}

	if(!Rounded)
		Graphics()->QuadsEnd();
}
