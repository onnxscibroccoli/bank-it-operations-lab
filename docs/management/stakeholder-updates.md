# Sample stakeholder communications (synthetic)

> **Synthetic / portfolio lab only.** Messages, people and times are invented and follow the
> scenarios in the other documents. Agents/bots are not equivalent to real employees. See
> [DISCLAIMER.md](DISCLAIMER.md).

Principles used in every message:

- **Lead with impact and what the reader should do.** Technical detail comes after.
- **Always give the next update time,** and send an update at that time even if nothing has
  changed.
- **Separate facts from hypotheses.** Say "we believe" when that is what we know.
- **One owner per message.** The communications lead sends it; engineers keep fixing.
- **Fit the audience:** users need actions, business owners need impact and decisions,
  leadership needs risk, options and asks.

## 1. P1 incident: initial notice (to payments users and business owner, 09:00 ET)

> **Subject:** [P1] Payments approval app sign-in failing - INC-LAB-1041 - next update 09:30 ET
>
> **Impact:** Since about 08:15 ET, Payments team members cannot sign in to the payments approval
> app. Other systems are not affected as far as we know.
>
> **What you should do:** Please don't retry repeatedly, because repeated attempts can lock your
> account. Urgent approvals before 10:00 ET: call the Payments business owner, who has the
> documented manual fallback procedure.
>
> **What we're doing:** We believe a security policy change made at 07:30 ET today is blocking
> these sign-ins. We are preparing to reverse it.
>
> **Next update:** 09:30 ET, or sooner if service is restored.
>
> P02, Service Desk Lead, for the incident team

## 2. P1 incident: restored (09:10 ET)

> **Subject:** [P1 RESTORED] Payments approval app sign-in - INC-LAB-1041
>
> Sign-in has worked again since 09:02 ET. We reversed this morning's policy change at 08:55 ET.
> If you still can't sign in, sign out of all browser windows and try again, then call the desk on
> the usual number.
>
> The wire cut-off (16:00 ET) is not affected. We will review what happened on Thursday and send
> a short summary to the Payments business owner by Friday.

## 3. Leadership summary (to Head of Technology, same day 12:00 ET)

> **INC-LAB-1041 (P1), resolved.** From 08:15 to 09:02 ET (47 min), Payments users could not
> sign in. The cause was our own planned security change (CHG-LAB-3120). It used a list of trusted
> network locations that was out of date and missed last week's VPN change. We reversed the change
> using its prepared backout plan. There was no customer impact and no missed payments.
>
> **What we're changing:** our change review will check for related network/identity changes from
> the past 14 days and will re-check location data on the day of implementation. Owners and dates
> are in the PIR (Thursday).
>
> **Risk while open:** the high-risk sign-in block is off until the re-run (planned next week).
> MFA is still enforced for all users, so we consider the exposure low.
>
> **Ask:** none.

## 4. Planned change notice (to all staff, 2 business days ahead)

> **Subject:** Planned: improved sign-in protection, Tue 2026-11-17 07:30 ET
>
> **What changes:** sign-ins that our identity provider rates as high-risk will be blocked
> instead of only logged.
>
> **Will I notice?** Most people won't. If you see "blocked by policy" when signing in from your
> usual place, call the service desk. We will be monitoring closely until 10:00 ET.
>
> **Why:** this closes an audit finding and protects accounts from stolen-password attacks.

## 5. Project status (to sponsor, checkpoint #3)

> **LAB-PRJ-07 Database resilience uplift: Amber, recoverable.**
> M3 (point-in-time recovery test) moves from 11-17 to 11-24. The reasons were a P2 incident that
> took priority, plus an upgrade that was deferred out of the month-end freeze. The final date
> (12-18) is unchanged.
> **Decision needed today:** accept the slip (recommended, no cost), or one of two recovery
> options. Details are in the checkpoint. If M3 is not done by 11-24, I will come back with the
> resourcing option.

## 6. Trade-off / "polite no" (to the requester of REQ-LAB-2210)

> Hi, thanks for flagging the CFO office printer. We have logged it as low priority: one printer
> is affected and the shared printer by reception is working. We are dealing with an outage
> affecting the payments team this morning, and that has to come first.
>
> To print right now, choose **"FL3-Reception"** in the print dialog (2-minute guide attached).
> Someone will come by to clear the jam during the late-morning overlap, aiming for before 12:00.
> If a document has to be printed for a deadline, call us and we'll walk it over.

The message says no to "P1" without saying no to the person. It explains the reason, gives an
immediate workaround, sets a realistic time, and offers a route for a genuine deadline.

## 7. Weekly team update (internal, Monday after handover)

> **This week:** primary P07, secondary P06, duty manager P10, security P08.
> **Changes:** CHG-LAB-3131 (re-enable sign-in risk policy, Tue 07:30), SM-04 patching (Thu
> evening).
> **Watch:** month-end freeze starts Fri 11-27.
> **Thanks:** P08 and P06, for a calm and fast backout last Tuesday. The written backout plan is
> why it took 3 minutes.
> **Leave:** none. Coverage matrix shows level 2 in every domain except PostgreSQL (R1, project M4).
