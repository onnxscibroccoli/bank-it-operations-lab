import { loadPolicy } from './policy';

/** Feature flags / context shared by the app entrypoint and tests (no lookups, no account context). */
export const LAB_CONTEXT: Record<string, unknown> = {};

/** Parsed config/backup-policy.json (the single source of truth for names, regions and retention). */
export const POLICY = loadPolicy();
