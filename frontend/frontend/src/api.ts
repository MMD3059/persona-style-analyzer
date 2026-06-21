const BASE = 'http://127.0.0.1:8000';

export interface Tweet {
  id: string;
  account: string;
  content: string;
  likes?: number;
  retweets?: number;
}

export interface StyleProfile {
  account: string;
  full_name?: string;
  bio?: string;
  vocab: {
    repeated_phrases: string[];
    religious_terms: string[];
    hashtag_patterns: string[];
    unique_terms: string[];
    sentence_length_avg?: number;
    formality_markers: string[];
  };
  tone: {
    formality: number;
    sentiment: string;
    emotional_range: string[];
    punctuation_style?: any;
    emoji_usage?: any;
  };
  beliefs: {
    core_values: string[];
    stances: Record<string, string>;
    authority_references: string[];
    in_group_vs_out_group?: string;
  };
  red_flags: {
    trigger_topics: string[];
    avoided_phrases: string[];
    typical_deflections: string[];
    sensitive_areas: string[];
  };
  created_at: string;
  model: string;
}

export interface ExtractionResponse {
  profile: StyleProfile;
  confidence: number;
  tweet_count: number;
}

export interface VerificationResponse {
  account: string;
  similarity_score: number;
  is_consistent: boolean;
  details: Record<string, any>;
}

export interface GenerationResponse {
  text: string;
  account: string;
  style_adherence: number;
}

async function req<T>(path: string, method = 'GET', body?: any): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(err.detail || 'Request failed');
  }
  return res.json();
}

export const api = {
  extract: (account: string, tweets: Tweet[], full_name?: string, bio?: string) =>
    req<ExtractionResponse>('/extract', 'POST', { account, tweets, full_name, bio }),

  verify: (account: string, text: string) =>
    req<VerificationResponse>('/verify', 'POST', { account, text }),

  generate: (account: string, prompt: string, max_tokens = 500) =>
    req<GenerationResponse>('/generate', 'POST', { account, prompt, max_tokens }),

  listProfiles: () =>
    req<{ profiles: { account: string; created_at: string; confidence: number }[]; count: number }>('/profiles'),

  getProfile: (account: string) =>
    req<StyleProfile>(`/profiles/${account}`),
};
