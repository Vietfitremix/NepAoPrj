import { api } from './api';
import type { Weather } from '../types';
export const getWeather = (city: string, signal?: AbortSignal) => api.get<Weather>('/weather', { params: { city }, signal }).then(r => r.data);
