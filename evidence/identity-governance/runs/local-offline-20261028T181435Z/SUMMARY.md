# Identity governance -- offline evidence run `local-offline-20261028T181435Z`

> **OFFLINE / SYNTHETIC EVIDENCE. Generated from local Microsoft Graph-shaped JSON fixtures in this repository. No Microsoft Entra ID tenant, Microsoft Graph API, AWS account or credential was used. Nothing here describes or claims the configuration or state of any tenant or account.**

| Field | Value |
|---|---|
| Mode | `offline-synthetic` |
| Tenant state claimed | `false` |
| Validated commit | `bfa875ed7f910af776ef0f7516513ed1c1934e73` |
| Branch | `identity-governance` |
| Scoped source tree clean at run | `true` |
| Started (UTC) | 2026-10-28T18:14:35Z |
| Finished (UTC) | 2026-10-28T18:14:36Z |
| Python | 3.13.5 |
| Overall | **PASS** |

## Commands

| # | Step | Expected exit | Exit | Result | Log |
|---|---|---|---|---|---|
| 1 | `python_version` | 0 | 0 | PASS | `logs/01_python_version.log` |
| 2 | `fixtures_drift_check` | 0 | 0 | PASS | `logs/02_fixtures_drift_check.log` |
| 3 | `unit_tests` | 0 | 0 | PASS | `logs/03_unit_tests.log` |
| 4 | `inventory_baseline` | 0 | 0 | PASS | `logs/04_inventory_baseline.log` |
| 5 | `inventory_findings` | 1 | 1 | PASS | `logs/05_inventory_findings.log` |
| 6 | `inventory_missing_fields` | 1 | 1 | PASS | `logs/06_inventory_missing_fields.log` |
| 7 | `inventory_auth_401` | 2 | 2 | PASS | `logs/07_inventory_auth_401.log` |
| 8 | `inventory_auth_403` | 2 | 2 | PASS | `logs/08_inventory_auth_403.log` |
| 9 | `inventory_throttled_recover` | 0 | 0 | PASS | `logs/09_inventory_throttled_recover.log` |
| 10 | `inventory_throttled_exhausted` | 2 | 2 | PASS | `logs/10_inventory_throttled_exhausted.log` |
| 11 | `inventory_paging_loop` | 2 | 2 | PASS | `logs/11_inventory_paging_loop.log` |
| 12 | `inventory_malformed_page` | 2 | 2 | PASS | `logs/12_inventory_malformed_page.log` |
| 13 | `inventory_free_tier` | 0 | 0 | PASS | `logs/13_inventory_free_tier.log` |
| 14 | `access_review_baseline` | 1 | 1 | PASS | `logs/14_access_review_baseline.log` |

## Inventory scenarios

| Scenario | Overall | Exit | Rows | Findings (H/M/L/I) | Graph pages | Retries | Error |
|---|---|---|---|---|---|---|---|
| `baseline` | PASS | 0 | 16 | 0/0/0/0 | 10 | 0 |  |
| `findings` | FINDINGS | 1 | 22 | 8/4/1/0 | 10 | 0 |  |
| `missing-fields` | FINDINGS | 1 | 14 | 2/4/3/0 | 10 | 0 |  |
| `auth-401` | ERROR | 2 | - | - | 0 | 0 | authorization 401 |
| `auth-403` | ERROR | 2 | - | - | 7 | 0 | authorization 403 |
| `throttled-recover` | PASS | 0 | 16 | 0/0/0/0 | 10 | 3 |  |
| `throttled-exhausted` | ERROR | 2 | - | - | 5 | 4 | throttled 429 |
| `paging-loop` | ERROR | 2 | - | - | 8 | 0 | response  |
| `malformed-page` | ERROR | 2 | - | - | 2 | 0 | response  |
| `free-tier` | PASS | 0 | 7 | 0/0/0/1 | 7 | 0 |  |

## Access review (baseline fixture)

Overall **FINDINGS** (exit 1); decisions {"Approve": 2, "Deny": 2, "NotReviewed": 1, "DontKnow": 0}; findings AR-002, AR-003, AR-001

## Input hashes (SHA-256)

| Kind | Path | SHA-256 |
|---|---|---|
| doc | `docs/federation/README.md` | `1eb823f7c65ab246a54d0f1804c108eda195dbc25cb5b86f89571f2e8daa55a0` |
| doc | `docs/federation/entra-to-aws-iam-identity-center.md` | `dfc833ccfb0c779b7a2ae12e73b471da1095a5030f0bbcb332ef0e66e606b1d8` |
| doc | `docs/federation/saml-vs-scim.md` | `7c117381c8b5cb164a55fb3d2e839e70682d02b3565fded34b727119819fd653` |
| evidence-generator | `evidence/identity-governance/README.md` | `72a6f330ab50e5efea5ccf53917e91354bcb2b93cb22b02d1f66fd95ab78b6e9` |
| evidence-generator | `evidence/identity-governance/generate_evidence.py` | `dc2d7ef1bb12c01804b0db659673ebe88472fb411979df21cd9598c5a2172748` |
| doc | `identity/governance/.gitignore` | `862263fa1f46c20f0d1e4dac5ffcc75abd55c08211b2c3864c5f8764b9d87793` |
| doc | `identity/governance/README.md` | `52dfec04efcc113819ddb6b7087b26e7b519259f88ffba1f6edce0a66f6b71fa` |
| tool | `identity/governance/access_review.py` | `31217174bb9279dfa34f19b86a98b4804dba9225c6879191ad212a499a10661c` |
| tool | `identity/governance/baseline.json` | `086955c1a33edf8bdd38aacb850c17c647b69fd323ebba3b669b7afc2176256a` |
| doc | `identity/governance/docs/access-review-lifecycle.md` | `e9b47c5cbb4f1c6ab9fc71033af6bffa507e4ef767d6857edecfaede6403b754` |
| doc | `identity/governance/docs/emergency-access-break-glass.md` | `6fe5bcb6bcac617fb32d844679a35cc3794d039db115442ec2bc95008babc8f3` |
| doc | `identity/governance/docs/licensing-prerequisites.md` | `4160a35fa029191187c5edff51adbeacb0a35d3e6875f250a607824084d10329` |
| doc | `identity/governance/docs/pim-lifecycle.md` | `d552b5dbd5b63a39b51f6f0b378793a053dcd76a661fae603317a523202cb2ef` |
| fixture | `identity/governance/fixtures/graph/scenarios/auth-401/routes.json` | `4a00ae4a70000492eef3fd2112e1e1ecd2ecbc9c1300ddaf717249338a375f0f` |
| fixture | `identity/governance/fixtures/graph/scenarios/auth-403/routes.json` | `bf5366c0d887274e228d3e6d5edde5f070afa74828773cdceb12f9ab27d55152` |
| fixture | `identity/governance/fixtures/graph/scenarios/baseline/accessReviewDecisions.page1.json` | `733dd5d2f9c6e67889da50591541e0d27d3f7411ab1deaad8a0d2f4e8df51bf9` |
| fixture | `identity/governance/fixtures/graph/scenarios/baseline/accessReviewDecisions.page2.json` | `b1f07ae16e6ca442db1c835e1017527c01d321339aae0b83b789420a898f55a3` |
| fixture | `identity/governance/fixtures/graph/scenarios/baseline/active.page1.json` | `e24bcab7d0333353f79f7ed70c24775df94ed2defaf037c9fc5bb508d20ef07b` |
| fixture | `identity/governance/fixtures/graph/scenarios/baseline/active.page2.json` | `87f90d3cad9dcffd359f6e6d229b432eb3ee32d0de14d11d10e49504b2ee1987` |
| fixture | `identity/governance/fixtures/graph/scenarios/baseline/eligible.page1.json` | `cbcd44863b6588596cc876060f5a34bfad8f32ca07f06b962396eafa8c6d8c3e` |
| fixture | `identity/governance/fixtures/graph/scenarios/baseline/eligible.page2.json` | `89a2055797b480a19743661871289b7e9867d6725ea5250d22486e051d6e9279` |
| fixture | `identity/governance/fixtures/graph/scenarios/baseline/eligible.page3.json` | `aa754ec692559139e7f8033e053918649ea84569874737fa78eafbb696d6d672` |
| fixture | `identity/governance/fixtures/graph/scenarios/baseline/groups.page1.json` | `cfacec119ec6af2639c5e56f6b2e55e3adba4806896aac4656ee8eb571e59869` |
| fixture | `identity/governance/fixtures/graph/scenarios/baseline/roleDefinitions.page1.json` | `033fc6148a7cb7cb3bbd7d7eed0b8652e4d4440a9ee0df6570ed731249f1d528` |
| fixture | `identity/governance/fixtures/graph/scenarios/baseline/routes.json` | `fde31f7c33f0260f0c741835ab6f20aa10d264f1668c2854f743110acb377779` |
| fixture | `identity/governance/fixtures/graph/scenarios/baseline/servicePrincipals.page1.json` | `209d893ec1027807c89ed767e6897636516cab424a4f9a8208328276e1703ea9` |
| fixture | `identity/governance/fixtures/graph/scenarios/baseline/users.page1.json` | `d181630cb7d95432da173be7c406ec27bdaa6046daabf5384b719a4839d8b64b` |
| fixture | `identity/governance/fixtures/graph/scenarios/baseline/users.page2.json` | `db0d728fb1280b38a5b7f17e3b3cf425fcecac6f75267cb945c323773231c29c` |
| fixture | `identity/governance/fixtures/graph/scenarios/findings/active.page1.json` | `4f4410d02ed9d03fe14689f5cb9ea5f8bb7366f7b7023bd496cd7a677f92afa9` |
| fixture | `identity/governance/fixtures/graph/scenarios/findings/active.page2.json` | `d77c4960b8c132f0b2df1e73165ac1b0749a64228f394196803d731350301f70` |
| fixture | `identity/governance/fixtures/graph/scenarios/findings/active.page3.json` | `12d3cc39c4d63b6a1f58b65f777742d9c5ba842471f4603462d78cb6cf02d0f8` |
| fixture | `identity/governance/fixtures/graph/scenarios/findings/eligible.page1.json` | `b2eb89efc2edab7aaf316899977faef274c7f7839b48766865e6d1ba97e732ad` |
| fixture | `identity/governance/fixtures/graph/scenarios/findings/eligible.page2.json` | `f9a10743f1a958e3989b5d0876b94f3c22b26d1c15cc70339215234d0b7d1359` |
| fixture | `identity/governance/fixtures/graph/scenarios/findings/routes.json` | `a3fc3b7874ac2b3f892fe7eca49732027709a3371685bd7332b2415105adc814` |
| fixture | `identity/governance/fixtures/graph/scenarios/findings/servicePrincipals.page1.json` | `cd4d752e4707e74343d68331b8340403504a3744d30f5706362df5fa076a2a10` |
| fixture | `identity/governance/fixtures/graph/scenarios/findings/users.page1.json` | `3bd784d8dbafbf278d437cc6d9100055bf445c58437ad149126dc7b7ffdbe5d7` |
| fixture | `identity/governance/fixtures/graph/scenarios/findings/users.page2.json` | `a53c94657876c1ae3e6df95c56e4c7cb3454f0d3275ff22d47300180d447806a` |
| fixture | `identity/governance/fixtures/graph/scenarios/free-tier/assignments.page1.json` | `93d4555a0ef7343f58cb72cb60c9852c30c795beb2812a02f96484215e6f5c3a` |
| fixture | `identity/governance/fixtures/graph/scenarios/free-tier/assignments.page2.json` | `e6bf475d6a090490884cb75d184bcaac9c023c6659ba5089d45c6878b1382873` |
| fixture | `identity/governance/fixtures/graph/scenarios/free-tier/routes.json` | `1019bd7c314d9f64f25e021b367c3c5b7f6f9df7e177466de8dec33c13ecac2f` |
| fixture | `identity/governance/fixtures/graph/scenarios/malformed-page/routes.json` | `bbefd3ab5274808cae6539ebf31fbac068a9d60013b51325d9e87af3bf83e0c0` |
| fixture | `identity/governance/fixtures/graph/scenarios/missing-fields/active.page1.json` | `a3cfe5047b02f5a4993d271ec248afa1d3a21a6aced78f32aba1361f2fa3d99f` |
| fixture | `identity/governance/fixtures/graph/scenarios/missing-fields/active.page2.json` | `b1906557ed3a182027daaf4d4b8fa80c85566c5ff29f07b4ce7f3eae65a813a6` |
| fixture | `identity/governance/fixtures/graph/scenarios/missing-fields/active.page3.json` | `2eece518650b4fd096c83aa0817ea640d67c2b325fac008e28d3422fe2d7014e` |
| fixture | `identity/governance/fixtures/graph/scenarios/missing-fields/routes.json` | `c96465011b26581ff078371d58b53f3796a9b3c78c405b43035ebd041b63d414` |
| fixture | `identity/governance/fixtures/graph/scenarios/missing-fields/users.page1.json` | `dc4b4f77b01387d7f3be51d4e6a3a71230152dd41894c16bb9354dd9bb6790ea` |
| fixture | `identity/governance/fixtures/graph/scenarios/paging-loop/eligible.loop.json` | `f6e3558791225cdb68296698f37fa764e4ae811f1b435f2d6a5c4b3697ca8874` |
| fixture | `identity/governance/fixtures/graph/scenarios/paging-loop/routes.json` | `dadbb66537f63959eb185b5fd2767d4c3b39107d4592294522ae375c3b4c7ba2` |
| fixture | `identity/governance/fixtures/graph/scenarios/throttled-exhausted/routes.json` | `807680879b369633fd926ad95342b451d454c1cb359484306aae8bfc07b0e58c` |
| fixture | `identity/governance/fixtures/graph/scenarios/throttled-recover/routes.json` | `45efd1b68b1f773bf5147517d64cee1df7093c382d3283504350cc8c8a778f61` |
| tool | `identity/governance/graph_client.py` | `bf9b418c7b1c1d8e3c6998a1d49becf49aaf0bf2e129b44eb8334adf4282afa6` |
| tool | `identity/governance/inventory.py` | `f61ed15635d3b85a4bbe60bdb74a8073296dcb34ce9975445df53e97a158ca75` |
| tool | `identity/governance/make_fixtures.py` | `55ac97beab94e469128d25e9d6d4a60a6ec57d08fd15dc18b218e40030ab09a8` |
| test | `identity/governance/tests/_common.py` | `bf09a09ef15a4e60df07a4a0c2833b834087e8559b2a6015e55bbfa86b983c3b` |
| test | `identity/governance/tests/test_access_review.py` | `e38faaab4df786c7101b7274bc2db67736cb14ee21974e1c979cd0e99f56127f` |
| test | `identity/governance/tests/test_graph_client.py` | `d2bae49b4bd6462c188fa6d10d9fd708d62f28b22b073701fc0f7ef7ee1f0f8c` |
| test | `identity/governance/tests/test_inventory.py` | `529a28c38f383d1523b9a818e846d5969d4412d8bc332a3256313d1e4d019786` |
| test | `identity/governance/tests/test_synthetic_guard.py` | `03806c6c35f34cb6441520e6a5c605537561e9c6cf33b4a70988b4303e4dc75b` |

Verify: `python3 evidence/identity-governance/generate_evidence.py --verify evidence/identity-governance/runs/local-offline-20261028T181435Z`
