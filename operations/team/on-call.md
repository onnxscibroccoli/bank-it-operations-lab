# Coverage and on-call (synthetic)

> **Synthetic / portfolio lab only.** Example rota for placeholder personas. Real on-call
> arrangements must follow the organization's HR policy and local working-time and compensation
> rules. Agents/bots are not equivalent to real employees.

## Service desk shifts (business days, ET)

| Shift | Hours (ET) | Staffed by | Cover if absent |
|---|---|---|---|
| Early | 07:30-16:00 | P03 | P02, then P10 (level 1) |
| Late | 09:30-18:00 | P04 | P02, then P10 (level 1) |
| Overlap | 09:30-16:00 | P03 + P04 + P02 | - |

Outside 07:30-18:00 ET, calls to the desk number go to an out-of-hours message that routes **P1/P2
only** to the technical on-call engineer through the paging tool. P3/P4 are logged by the portal
and picked up the next business day.

## On-call tiers

| Tier | Who | Pool | Acknowledge page within | Role |
|---|---|---|---|---|
| Primary technical | 1 engineer per week | P05, P06, P07, P08 | 15 min (P1), 30 min (P2) | First technical responder for any infrastructure service; pulls in the domain owner if outside own skills |
| Secondary technical | Previous week's primary | same | 15 min after primary misses or requests | Backup if primary does not acknowledge, and second pair of hands on P1 |
| Duty manager | 1 per week | P01, P02, P10 | 30 min | Incident commander for P1 out of hours, stakeholder updates, emergency change approval |
| Security on-call | 1 per week | P09 (P08 when off technical rota) | 15 min | Security alerts and suspected security incidents; MSSP retainer as overflow |

## Rotation rules

1. Weekly handover **Monday 09:00 ET** (a business-hours handover avoids handing over mid-night).
2. Primary week is followed by a secondary week, then **two weeks with no technical on-call**.
   With four engineers each person is primary 1 week in 4.
3. Nobody holds primary technical and security on-call in the same week.
4. Swaps are allowed if both people agree, the swap keeps rule 3, and P10 updates the rota at least
   48 hours ahead.
5. Fatigue limit: if an engineer is paged out of hours for more than 2 hours in a night, they start
   no earlier than 4 hours later the next day; three or more such nights in one week triggers a
   review of the alert source at the next operational review.
6. Public holidays: change freeze applies; the person on primary gets a compensating day off.

The concrete example rota is [`oncall-rotation.csv`](oncall-rotation.csv) (weeks starting
2026-11-02). Known imbalance: P09 carries security on-call in 6 of 8 weeks. Volume is low and the
MSSP retainer absorbs overflow, but this is tracked as coverage risk R2 in
[`team-model.md`](team-model.md) until P05 is trained as a second security backup.

## Handover checklist (Monday 09:00 ET)

- Open P1/P2 incidents and their next update time
- Changes scheduled in the coming week (from the CAB calendar) and any freeze windows
- Alerts that fired more than 3 times last week (candidates for tuning)
- Known leave and the cover arrangement (from the coverage matrix)
- Paging tool test: outgoing primary triggers a test page to incoming primary and secondary
