import { BASELINE_SCP_IDS } from './scps';

/** Reference OU layout (AWS multi-account strategy style). `parent` undefined = organization root. */
export interface OuSpec {
  key: string;
  name: string;
  parent?: string;
  scps: string[];
}

export const OU_LAYOUT: OuSpec[] = [
  { key: 'Security', name: 'Security', scps: BASELINE_SCP_IDS },
  { key: 'Infrastructure', name: 'Infrastructure', scps: BASELINE_SCP_IDS },
  { key: 'Workloads', name: 'Workloads', scps: BASELINE_SCP_IDS },
  { key: 'WorkloadsProd', name: 'Prod', parent: 'Workloads', scps: [] },
  { key: 'WorkloadsNonProd', name: 'NonProd', parent: 'Workloads', scps: [] },
  { key: 'Sandbox', name: 'Sandbox', scps: BASELINE_SCP_IDS },
  { key: 'Suspended', name: 'Suspended', scps: ['deny-all-suspended'] },
];
