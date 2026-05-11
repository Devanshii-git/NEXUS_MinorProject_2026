const GROUP_KEYS = ['clusters', 'requirement_groups', 'groups', 'result', 'data'];

function parseJSONStringSafely(value) {
  if (typeof value !== 'string') return value;

  try {
    return JSON.parse(value);
  } catch {
    return value;
  }
}

function unwrapResponsePayload(input) {
  let payload = parseJSONStringSafely(input);

  // Handle repeated wrapping/double-encoded payloads defensively.
  for (let i = 0; i < 4; i += 1) {
    if (typeof payload === 'string') {
      const parsed = parseJSONStringSafely(payload);
      if (parsed === payload) break;
      payload = parsed;
      continue;
    }

    if (payload && typeof payload === 'object') {
      const nested =
        payload.response ??
        payload.payload ??
        payload.data ??
        payload.result ??
        payload.body;

      if (!nested || nested === payload) break;
      payload = parseJSONStringSafely(nested);
      continue;
    }

    break;
  }

  return payload;
}

export function getResponseGroups(response) {
  const payload = unwrapResponsePayload(response);

  if (Array.isArray(payload)) return payload;
  if (!payload || typeof payload !== 'object') return [];

  for (const key of GROUP_KEYS) {
    const candidate = payload?.[key];
    if (Array.isArray(candidate) && candidate.length > 0) {
      return candidate;
    }
  }

  return [];
}

export function parseAndNormalizeResponse(response) {
  const payload = unwrapResponsePayload(response);
  const groups = getResponseGroups(payload);

  const message =
    payload?.message ||
    payload?.statusMessage ||
    (groups.length > 0 ? `Detected ${groups.length} cluster(s).` : 'No analysis groups detected.');

  const metadata = {
    totalRequirements:
      payload?.metadata?.total_requirements ??
      payload?.total_requirements ??
      groups.reduce((sum, g) => sum + (Array.isArray(g?.requirements) ? g.requirements.length : 0), 0),
    totalClusters:
      payload?.metadata?.total_clusters ??
      payload?.cluster_count ??
      payload?.requirement_group_count ??
      groups.length,
    generatedAt: payload?.metadata?.generated_at ?? null,
  };

  if (!groups.length) {
    console.warn('[ResultsParser] Unsupported/empty response structure:', payload);
  }

  return {
    payload,
    groups,
    message,
    metadata,
  };
}
