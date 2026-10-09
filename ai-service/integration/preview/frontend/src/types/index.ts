export interface Weather { city: string; temperature: number; condition: string; humidity: number }
export interface Preferences { prompt: string; eventCode: string; styleCode: string; colorCode: string; city: string; weather: Weather }
export interface Asset { id: string; url: string; colorCode?: string; zIndex?: number; label?: string }
export interface Option { code: string; label: string; hex?: string }
export interface Accessory extends Option { assetUrl: string; zIndex?: number }
export interface Outfit { code: string; name: string; baseAvatarUrl: string; assets: Asset[]; colors: Option[]; styles: Option[]; accessories: Accessory[]; otherLayers?: Asset[] }
export interface Concept { id: string; name: string; outfitCode: string; outfitName: string; imageUrl: string; colorCode: string; colorName: string; styleCode: string; styleName: string; matchScore: number; reason: string; accessoryCodes?: string[] }
export interface Recommendation { id: string; understanding: string; concepts: Concept[] }
export interface CulturalKnowledge { name: string; origin: string; meaning: string; characteristics: string; sources?: { title: string; url: string }[] }
export interface MixConfig { conceptId: string; outfitCode: string; colorCode: string; styleCode: string; eventCode: string; accessoryCodes: string[] }
export interface Changes { colorCode?: string; styleCode?: string; removeAccessories?: string[]; addAccessories?: string[] }
export interface CulturalResult { score: number | null; level: string; warnings: { severity: string; category: string; message: string; suggestion: string; changes?: Changes }[] }
export interface RemixResult { changes: Changes; explanation: string }
export interface Look { id: string; name: string; imageUrl: string; outfitCode: string; outfitName: string; styleName: string; eventName: string; matchScore: number | null; culturalScore: number | null; colorHarmony: number | null; config: MixConfig; culturalKnowledge?: CulturalKnowledge }
