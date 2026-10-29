import { App, Aspects, Stack } from 'aws-cdk-lib';
import { Annotations, Match, Template } from 'aws-cdk-lib/assertions';
import { AwsSolutionsChecks } from 'cdk-nag';
import { Construct } from 'constructs';
import { LAB_CONTEXT } from '../lib/lab-context';

export function synth<T extends Stack>(make: (scope: Construct) => T): { stack: T; template: Template } {
  const app = new App({ context: LAB_CONTEXT });
  const stack = make(app);
  Aspects.of(stack).add(new AwsSolutionsChecks({ verbose: true, reports: false }));
  app.synth();
  return { stack, template: Template.fromStack(stack) };
}

export function nagErrors(stack: Stack) {
  return Annotations.fromStack(stack).findError('*', Match.stringLikeRegexp('AwsSolutions-.*'));
}
