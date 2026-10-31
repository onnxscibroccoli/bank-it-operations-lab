# Publish the knowledge base with GitHub Pages

GitHub Pages serves prepared website files. This project builds those files with its own documentation workflow, so the publishing source must be GitHub Actions rather than a branch folder.

## One-time repository setting

1. Open <https://github.com/onnxscibroccoli/bank-it-operations-lab/settings/pages> while signed in as the repository owner.
2. Under **Build and deployment**, open **Source**.
3. Select **GitHub Actions**. GitHub normally saves that selection immediately.
4. Do not add a second suggested Jekyll or framework workflow; the repository already supplies its documentation workflow.

The connected GitHub integration used for development does not expose Pages administration. The standard workflow token cannot enable a previously disabled Pages site through configure-pages. This one-time setting therefore needs the owner’s UI access; do not paste a personal access token into documentation or chat.

## Publish after integration

1. Open the repository’s **Actions** tab.
2. Select **Documentation knowledge base**.
3. Select **Run workflow**, choose **main**, enable **deploy**, and run it.
4. Wait for **validate** and **deploy** to succeed. If the github-pages environment requires confirmation, approve that deployment in the run’s interface.
5. Open the page_url shown by the deploy job. The expected default address is <https://onnxscibroccoli.github.io/bank-it-operations-lab/>; it is not a confirmed live site until the deployment succeeds.

Once this workflow is on main, documentation pushes to main also attempt deployment after validation. If the one-time setting was not enabled yet, enable it and rerun the workflow as above.

## Verification and troubleshooting

Search for “How do I recover a database?” and “How do I control employee permissions?”. Confirm relevant results open correctly under the repository URL prefix. Tab through search and navigation and test the site on a phone. A missing page or failed deployment is not evidence that publication succeeded.

If configure-pages reports that the site cannot be found, confirm Settings → Pages → Source is GitHub Actions. If deploy reports a permission or environment problem, inspect the failed step and the github-pages environment’s branch restrictions. Do not remove safeguards or grant unrelated cloud permissions.

The workflow grants Pages write and identity-token permissions only to the deployment job. Pull requests build previews and reports without deploying. Publication does not contact AWS, Microsoft tenants, or the lab’s production-like example services.

## Local preview

Use the commands in [the development guide](development.md). Serve dist/docs over local HTTP; opening index.html directly as a file can prevent browser search from loading its index. Stop the local server with Ctrl+C. No public hosting or paid API is required for a local preview.

## References

[GitHub publishing-source instructions](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site) and [configure-pages inputs](https://github.com/actions/configure-pages/blob/main/action.yml) describe the source setting and enablement limitation.
