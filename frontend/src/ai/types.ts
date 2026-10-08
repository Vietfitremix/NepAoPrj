// Kiểu dữ liệu của AI Nếp Áo (khớp /ai/catalog, /ai/quiz, /ai/stylist, /ai/evaluate, /ai/review)
export interface Named { id: string; name: string }
export interface Garment extends Named { genders: string[]; hasSvg?: boolean }
export interface Colour extends Named { hex: string }
export interface Accessory extends Named { slot: string; genders: string[]; byGender?: boolean; usesAccent?: boolean }
export interface Pattern extends Named { tile?: number; motif: string; kind?: string; group?: string; note?: string; garments?: string[]; genders?: string[] }
export interface CultureCard { garmentId: string; title: string; body: string; verified?: boolean }
export interface ChecklistData { garments?: Record<string, string>; bottoms?: Record<string, string>; accessories?: Record<string, string>; lining?: string }
export interface RawCatalog {
  garments: Garment[]; colors: Colour[]; accessories: Accessory[]; patterns: Pattern[]; occasions: Named[]; styles: Named[];
  cultureCards: CultureCard[]; checklist?: ChecklistData;
}
export interface Catalog extends RawCatalog {
  color: Record<string, Colour>; acc: Record<string, Accessory>; garment: Record<string, Garment>; pattern: Record<string, Pattern>;
  occasion: Record<string, Named>; style: Record<string, Named>;
}
export interface QuizOption { value: string; label: string; hex?: string }
export interface QuizQuestion { id: string; field: string; question: string; type: 'single' | 'multi'; required?: boolean; options: QuizOption[]; placeholder?: string }
export interface Answer { value?: string | string[] | null; text?: string }
export interface Colors { main: string; bottom: string; lining?: string | null; accent?: string | null }
export interface OutfitState { garment: string; gender: string; occasion: string; style: string; pattern?: string; colors: Colors; accessories: string[] }
export interface Criterion { id: string; name: string; en?: string; weight: number; score: number; ruleIds: string[]; notes: string[] }
export interface ScoreCard { total: number; band: 'chuan_bo' | 'hop_dip' | 'can_chinh'; bandText: string; capped?: boolean; criteria: Criterion[] }
export interface Suggestion { text: string; patch?: Record<string, unknown> | null }
export interface Evaluation { ruleId?: string; level: 'ok' | 'consider' | 'risk'; reason: string; suggestion: Suggestion }
export interface StylistOutfit { outfitId: string; state: OutfitState; evaluations: Evaluation[]; scoreCard?: ScoreCard | null; title: string; comment: string; tip: string; whyChosen?: string; changes?: string[] }
export type Context = Record<string, string | string[] | null | undefined>
export interface OutfitsResponse { kind: 'outfits'; intent: Context; outfits: StylistOutfit[]; source: string }
export interface ClarifyResponse { kind: 'clarify'; question: string; options: { label: string; occasion?: string | null }[] }
export interface StylistResult { loading?: boolean; res?: OutfitsResponse | ClarifyResponse; body?: Record<string, unknown>; ms?: number; error?: string }
export interface EvaluateResponse { evaluations: Evaluation[]; color: { score: number; note: string }; scoreCard: ScoreCard }
export interface ReviewResponse { verdict: 'hop' | 'nen_chinh'; verdictText: string; source: string; current: StylistOutfit; alternatives: StylistOutfit[] }
export interface SavedLook { state: OutfitState; context?: Context; scoreCard?: ScoreCard | null; note?: { title: string; comment: string; tip: string } }
