import type { CulturalKnowledge, CulturalSection } from '../types';

export interface KnowledgeRow {
  category: string; title: string; content: string;
  sourceName: string | null; sourceUrl: string | null;
}
const order = ['ORIGIN', 'CHARACTERISTICS', 'MEANING', 'WEARING', 'CONTEXT', 'PRESERVATION'];
export function culturalKnowledge(rows: KnowledgeRow[], outfit: {
  name: string; origin?: string | null; culturalMeaning?: string | null;
}): CulturalKnowledge {
  const sources = new Map<string, { title: string; url: string }>();
  const sections: CulturalSection[] = rows.filter(row => row.content.trim()).map(row => {
    const url = row.sourceUrl?.trim();
    const source = url && /^https?:\/\//i.test(url)
      ? { title: row.sourceName || row.title, url } : undefined;
    if (source && !sources.has(source.url)) sources.set(source.url, source);
    return { category: row.category, title: row.title,
      paragraphs: row.content.split(/\n\s*\n/).map(text => text.trim()).filter(Boolean), source };
  }).sort((a, b) => {
    const rank = (category: string) => {
      const index = order.indexOf(category);
      return index < 0 ? order.length : index;
    };
    return rank(a.category) - rank(b.category);
  });
  const content = (category: string) => sections.filter(section => section.category === category)
    .flatMap(section => section.paragraphs).join('\n\n');
  const unavailable = 'Chưa có dữ liệu được kiểm chứng.';
  return { name: outfit.name, sections, sources: [...sources.values()],
    origin: content('ORIGIN') || outfit.origin || unavailable,
    meaning: content('MEANING') || outfit.culturalMeaning || unavailable,
    characteristics: content('CHARACTERISTICS') || unavailable };
}
