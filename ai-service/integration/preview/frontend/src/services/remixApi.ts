import { api } from './api';
import type { MixConfig, RemixResult } from '../types';
import { selection } from './backendContract';
export { applyChanges } from '../utils/mix';
export const remix = (config: MixConfig, prompt: string) => api.post<RemixResult>('/remix', {
  currentLook: selection(config), prompt }).then(r => r.data);
