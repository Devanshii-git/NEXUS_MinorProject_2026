import { createContext, useContext, useState, useCallback, useMemo } from 'react';
import { getResponseGroups, parseAndNormalizeResponse } from '../utils/resultsParser';

const ResultsContext = createContext(null);

// ─────────────────────────────────────────────────────────────────────────────
// Normalization Layer
// Handles ALL known JSON response formats from the NLP pipeline:
//   Format A: { clusters: [...] }                 (jsonformatter.txt, (1), (2))
//   Format B: { requirement_groups: [...] }       (legacy output format)
//   Format C: raw array [...]                     (edge case)
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Normalize a single requirement object to a unified shape.
 * Handles missing fields, different entity formats, and nested priority data.
 */
function normalizeRequirement(req, group, groupIndex) {
  if (!req) return null;

  // Resolve the final priority — check semantic_correction → final_arbitration → direct
  const finalPriority =
    req?.final_arbitration?.final_priority ||
    req?.semantic_correction?.final_priority ||
    req?.priority ||
    group?.cluster_priority ||
    group?.priority ||
    'LOW';

  // Resolve the priority score
  const priorityScore =
    req?.priority_score ??
    group?.cluster_priority_score ??
    0;

  // Collect priority reasons from all available sources
  const priorityReasons = [
    ...(req?.priority_reasons || []),
    ...(req?.semantic_correction?.reason || []),
    ...(req?.final_arbitration?.reason || []),
  ].filter(Boolean);

  // Resolve requirement type from structured data or direct field
  const requirementType =
    req?.structured?.requirement_type ||
    req?.requirement_type ||
    'functional';

  // Normalize entity data — API returns either:
  //   { entities: [{ text, label }] }  (array of entity objects)
  //   { entities: { actors: [], features: [], ... } }  (grouped object — legacy)
  const entitiesArray = Array.isArray(req?.entities) ? req.entities : [];
  const groupedEntities = req?.grouped || {};

  // Build a unified entities object from either format
  const features = groupedEntities.FEATURE || entitiesArray.filter(e => e?.label === 'FEATURE').map(e => e.text) || [];
  const actors = groupedEntities.ACTOR || entitiesArray.filter(e => e?.label === 'ACTOR').map(e => e.text) || [];
  const actions = groupedEntities.ACTION || entitiesArray.filter(e => e?.label === 'ACTION').map(e => e.text) || [];
  const qualityAttrs = groupedEntities.QUALITY_ATTRIBUTE || entitiesArray.filter(e => e?.label === 'QUALITY_ATTRIBUTE').map(e => e.text) || [];
  const constraints = groupedEntities.CONSTRAINT || entitiesArray.filter(e => e?.label === 'CONSTRAINT').map(e => e.text) || [];
  const priorityIndicators = groupedEntities.PRIORITY_INDICATOR || entitiesArray.filter(e => e?.label === 'PRIORITY_INDICATOR').map(e => e.text) || [];

  // Map priority string to UI-friendly format
  const priorityMap = { HIGH: 'High', MEDIUM: 'Medium', LOW: 'Low', CRITICAL: 'Critical' };
  const displayPriority = priorityMap[finalPriority?.toUpperCase()] || finalPriority || 'Low';

  // Generate a group ID — prefer existing, fallback to index-based
  const groupId = group?.group_id || `REQ-${String(groupIndex + 1).padStart(3, '0')}`;

  return {
    id: groupId,
    text: req?.sentence || req?.text || 'No requirement text available',
    type: requirementType === 'functional' ? 'Functional' :
          requirementType === 'non-functional' ? 'Non-Functional' : 'Ambiguous',
    priority: displayPriority,
    source: group?.cluster_name || group?.group_name || `Cluster ${groupIndex + 1}`,
    confidence: req?.confidence ?? 0,
    priorityScore: priorityScore,
    priorityReasons: priorityReasons.length > 0 ? priorityReasons : ['No priority signals detected'],
    structured: req?.structured || {},
    entities: {
      features,
      actors,
      actions,
      quality_attributes: qualityAttrs,
      constraints,
      priority_indicators: priorityIndicators,
    },
    explanation: req?.explanation || null,
    semanticCorrection: req?.semantic_correction || null,
    finalArbitration: req?.final_arbitration || null,
    rawGroup: group,
  };
}

/**
 * Shared state for NLP analysis results.
 * Populated by AI processing from Jira issues/comments.
 * Consumed by all Results sub-pages (Extracted, Classification, Clustering, Prioritization, Summary).
 */
export function ResultsProvider({ children }) {
  const [rawResponse, setRawResponse] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [source, setSource] = useState(null); // 'issues' | 'comments' | null

  // Store a new AI response
  const storeResults = useCallback((response, sourceType) => {
    try {
      const parsedResult = parseAndNormalizeResponse(response);
      const parsed = parsedResult.payload;

      console.log('[ResultsContext] Storing results:', {
        type: typeof parsed,
        keys: parsed && typeof parsed === 'object' ? Object.keys(parsed) : 'null',
        hasClusters: !!parsed?.clusters,
        hasRequirementGroups: !!parsed?.requirement_groups,
        clusterCount: parsedResult.groups.length,
      });

      setRawResponse(parsed);
      setSource(sourceType);
      setError(null);
    } catch (err) {
      console.error('[ResultsContext] Failed to process AI response:', err);
      setError('Failed to parse AI response');
    }
  }, []);

  const clearResults = useCallback(() => {
    setRawResponse(null);
    setSource(null);
    setError(null);
  }, []);

  // ─── Derived: flat list of all requirements ───────────────────────────────
  const allRequirements = useMemo(() => {
    const groups = getResponseGroups(rawResponse);
    if (groups.length === 0) return [];

    const reqs = [];
    groups.forEach((group, groupIndex) => {
      const requirements = group?.requirements || [];
      if (requirements.length === 0) {
        // Edge case: group has no requirements array — treat the group itself as a single requirement
        const fallbackReq = normalizeRequirement(
          { sentence: group?.cluster_summary || group?.summary || group?.cluster_name || 'Unknown requirement' },
          group,
          groupIndex
        );
        if (fallbackReq) reqs.push(fallbackReq);
        return;
      }

      requirements.forEach((req) => {
        const normalized = normalizeRequirement(req, group, groupIndex);
        if (normalized) reqs.push(normalized);
      });
    });

    return reqs;
  }, [rawResponse]);

  // ─── Derived: classification groups ───────────────────────────────────────
  const classificationGroups = useMemo(() => {
    const groups = { Functional: [], 'Non-Functional': [], Ambiguous: [] };
    allRequirements.forEach((req) => {
      if (groups[req.type]) {
        groups[req.type].push(req);
      }
    });
    return groups;
  }, [allRequirements]);

  // ─── Derived: clusters for ClusteringPage ─────────────────────────────────
  const clusters = useMemo(() => {
    const groups = getResponseGroups(rawResponse);
    if (groups.length === 0) return [];

    const palette = ['#6366f1', '#f59e0b', '#ef4444', '#10b981', '#06b6d4', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316', '#a855f7'];

    return groups.map((group, i) => {
      const groupId = group?.group_id || `REQ-${String(i + 1).padStart(3, '0')}`;
      const groupName = group?.cluster_name || group?.group_name || `Cluster ${i + 1}`;

      // Extract keywords from requirements' entities (handle both formats)
      const keywords = new Set();
      (group?.requirements || []).forEach((req) => {
        // New format: entities is array of { text, label }
        if (Array.isArray(req?.entities)) {
          req.entities.forEach((e) => {
            if (e?.text) keywords.add(e.text);
          });
        }
        // Also check grouped entities
        const grouped = req?.grouped || {};
        Object.values(grouped).forEach((vals) => {
          if (Array.isArray(vals)) vals.forEach((v) => keywords.add(v));
        });
        // Legacy format: entities is { features: [], actors: [], ... }
        if (req?.entities && !Array.isArray(req.entities)) {
          ['features', 'actors', 'actions', 'priority_indicators'].forEach((key) => {
            (req.entities[key] || []).forEach((v) => keywords.add(v));
          });
        }
      });

      return {
        id: groupId,
        name: groupName,
        color: palette[i % palette.length],
        keywords: [...keywords].slice(0, 5),
        summary: group?.cluster_summary || group?.summary || '',
        silhouetteScore: group?.silhouette_score ?? null,
        clusterPriority: group?.cluster_priority || group?.priority || 'LOW',
        clusterExplanation: group?.cluster_explanation || '',
        requirements: (group?.requirements || []).map((req) => ({
          id: groupId,
          text: req?.sentence || req?.text || 'No text',
          confidence: req?.confidence ?? 0,
        })),
      };
    });
  }, [rawResponse]);

  // ─── Derived: prioritized list (sorted by priority_score descending) ──────
  const prioritizedRequirements = useMemo(() => {
    return [...allRequirements].sort((a, b) => b.priorityScore - a.priorityScore);
  }, [allRequirements]);

  // ─── Derived: summary stats ───────────────────────────────────────────────
  const summaryStats = useMemo(() => {
    if (!rawResponse || allRequirements.length === 0) return null;

    const totalReqs = allRequirements.length;
    const parsedResult = parseAndNormalizeResponse(rawResponse);
    const groups = parsedResult.groups;
    const totalClusters = groups.length;
    const avgScore = totalReqs > 0
      ? (allRequirements.reduce((s, r) => s + r.priorityScore, 0) / totalReqs).toFixed(1)
      : '0';
    const funcCount = allRequirements.filter((r) => r.type === 'Functional').length;
    const nfCount = allRequirements.filter((r) => r.type === 'Non-Functional').length;
    const ambCount = allRequirements.filter((r) => r.type === 'Ambiguous').length;

    return {
      totalRequirements: totalReqs,
      totalClusters,
      avgPriorityScore: avgScore,
      functional: funcCount,
      nonFunctional: nfCount,
      ambiguous: ambCount,
      ambiguityRate: totalReqs > 0 ? ((ambCount / totalReqs) * 100).toFixed(0) : '0',
      message: parsedResult.message,
    };
  }, [rawResponse, allRequirements]);

  const hasResults = !!rawResponse && (allRequirements.length > 0 || getResponseGroups(rawResponse).length > 0);

  const value = {
    rawResponse,
    isLoading,
    setIsLoading,
    error,
    setError,
    source,
    storeResults,
    clearResults,
    hasResults,
    allRequirements,
    classificationGroups,
    clusters,
    prioritizedRequirements,
    summaryStats,
  };

  return <ResultsContext.Provider value={value}>{children}</ResultsContext.Provider>;
}

export function useResults() {
  const context = useContext(ResultsContext);
  if (!context) {
    throw new Error('useResults must be used within a ResultsProvider');
  }
  return context;
}

export default ResultsContext;
