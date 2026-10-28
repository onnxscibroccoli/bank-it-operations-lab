import { App, Aspects, Stack } from 'aws-cdk-lib';
import { Annotations, Match, Template } from 'aws-cdk-lib/assertions';
import { AwsSolutionsChecks, NIST80053R5Checks } from 'cdk-nag';
import { LAB_CONTEXT } from '../lib/lab-context';

export const NAG_PACKS = ['AwsSolutions', 'NIST.800.53.R5'] as const;

export function synthWithNag<T extends Stack>(make: (app: App) => T): { stack: T; template: Template } {
  const app = new App({ context: LAB_CONTEXT });
  const stack = make(app);
  Aspects.of(stack).add(new AwsSolutionsChecks({ verbose: true, reports: false }));
  Aspects.of(stack).add(new NIST80053R5Checks({ verbose: true, reports: false }));
  app.synth();
  return { stack, template: Template.fromStack(stack) };
}

export function nagFindings(stack: Stack, kind: 'error' | 'warning', pack: string) {
  const a = Annotations.fromStack(stack);
  const re = Match.stringLikeRegexp(`${pack.replace(/\./g, '\\.')}-.*`);
  return kind === 'error' ? a.findError('*', re) : a.findWarning('*', re);
}

/** Every cdk-nag suppression in the template, as {rule, logicalId}. */
export function suppressionsIn(template: Template): { rule: string; logicalId: string; path?: string; reason: string }[] {
  const out: { rule: string; logicalId: string; path?: string; reason: string }[] = [];
  for (const [id, r] of Object.entries<any>(template.toJSON().Resources ?? {})) {
    for (const s of r.Metadata?.cdk_nag?.rules_to_suppress ?? []) {
      out.push({ rule: s.id, logicalId: id, path: r.Metadata?.['aws:cdk:path'], reason: s.reason });
    }
  }
  return out;
}
