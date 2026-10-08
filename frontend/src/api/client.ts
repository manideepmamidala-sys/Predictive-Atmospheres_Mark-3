import type { paths } from './schema';

export type RoomInput = paths['/v1/predict']['post']['requestBody']['content']['application/json']['room'];
export type AffectTarget = paths['/v1/predict']['post']['requestBody']['content']['application/json']['target'];
export type PredictResponse = paths['/v1/predict']['post']['responses'][200]['content']['application/json'];
export type OptimizeRequest = paths['/v1/optimize']['post']['requestBody']['content']['application/json'];
export type OptimizeResponse = paths['/v1/optimize']['post']['responses'][200]['content']['application/json'];
export type MetaResponse = paths['/v1/meta']['get']['responses'][200]['content']['application/json'];

const baseUrl = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');

async function request<Response>(path: keyof paths, method: 'GET' | 'POST', body?: unknown): Promise<Response> {
  let response: globalThis.Response;
  try {
    response = await fetch(`${baseUrl}${path}`, {
      method, headers: body === undefined ? undefined : { 'Content-Type': 'application/json' },
      body: body === undefined ? undefined : JSON.stringify(body), signal: AbortSignal.timeout(20_000),
    });
  } catch {
    throw new Error('The prediction service could not be reached. Your inputs are preserved; try again when the service is available.');
  }
  const payload: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    const error = payload && typeof payload === 'object' && 'error' in payload ? payload.error : null;
    const message = error && typeof error === 'object' && 'message' in error && typeof error.message === 'string' ? error.message : `The prediction service returned HTTP ${response.status}.`;
    throw new Error(message);
  }
  if (!payload || typeof payload !== 'object' || !('schema_version' in payload)) {
    throw new Error('The prediction service returned an incompatible response.');
  }
  return payload as Response;
}

export const getMeta = () => request<MetaResponse>('/v1/meta', 'GET');
export const predictRoom = (room: RoomInput, target: AffectTarget) => request<PredictResponse>('/v1/predict', 'POST', { room, target } satisfies paths['/v1/predict']['post']['requestBody']['content']['application/json']);
export const optimizeRoom = (body: OptimizeRequest) => request<OptimizeResponse>('/v1/optimize', 'POST', body);
