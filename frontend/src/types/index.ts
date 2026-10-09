export interface Weather { city: string; temperature: number; condition: string; humidity: number }
import type { MaleSelection, WardrobeCharacter } from '../utils/maleWardrobe';
export interface QuizAnswer { value?: string | string[] | null; text?: string }
export interface Preferences { prompt: string; eventCode: string; styleCode: string; colorCode: string; city: string; weather: Weather; answers?: Record<string, QuizAnswer>; character?: WardrobeCharacter }
export interface Asset { id: string; url: string; colorCode?: string; zIndex?: number; label?: string }
export interface Option { code: string; label: string; hex?: string }
export interface Accessory extends Option { assetUrl: string; zIndex?: number; type?: string; description?: string }
export interface Outfit { code: string; name: string; baseAvatarUrl: string; assets: Asset[]; colors: Option[]; styles: Option[]; accessories: Accessory[]; otherLayers?: Asset[] }
export interface Concept { id: string; name: string; outfitCode: string; outfitName: string; imageUrl: string; colorCode: string; colorName: string; styleCode: string; styleName: string; matchScore: number; reason: string; accessoryCodes?: string[] }
export interface Recommendation { id: string; understanding: string; concepts: Concept[] }
export interface CulturalSection { category: string; title: string; paragraphs: string[]; source?: { title: string; url: string } }
export interface CulturalKnowledge { name: string; origin: string; meaning: string; characteristics: string; sections?: CulturalSection[]; sources?: { title: string; url: string }[] }
export interface MixConfig { conceptId: string; outfitCode: string; colorCode: string; styleCode: string; eventCode: string; accessoryCodes: string[]; wardrobe?: { character: WardrobeCharacter; selection: MaleSelection } }
export interface Changes { colorCode?: string; styleCode?: string; removeAccessories?: string[]; addAccessories?: string[] }
export interface CulturalResult { checks?: { ruleId:string; title:string; category:string; level:string; points:number; reason:string; suggestion:string }[]; assessment?: { ruleCount:number; matchedRuleCount:number; contextUsed:Record<string,string>; missingContext:string[]; colorMetrics:Record<string,number> }; score: number | null; level: string; breakdown?: {structure?:number;garmentCharacteristics?:number;accessories?:number;context?:number;modernRemix?:number}; explanation?:string; warnings: { severity: string; category: string; message: string; suggestion: string; sourceName?: string; sourceUrl?: string; sourceVerified?: boolean; sourceNote?: string; changes?: Changes }[] }
export interface RemixResult { changes: Changes; explanation: string }
export interface Look { id: string; name: string; imageUrl: string; outfitCode: string; outfitName: string; styleName: string; eventName: string; matchScore: number | null; culturalScore: number | null; colorHarmony: number | null; config: MixConfig; culturalKnowledge?: CulturalKnowledge }
