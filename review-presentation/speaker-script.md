# CON-1187: proving the Host docs in practice

Revised script: 776 spoken words across 12 scenes. Only the Spoken script paragraphs are the narration payload.

## 1. Useful instructions, checked against real behaviour

**On screen:** Start with the ticket. Then follow the updated Host docs and their evidence.

**Spoken script**

CON eleven eighty seven asked for clearer and more useful Host docs. The related tickets covered setup, account access, daily operations, and error guidance. We updated those pages, then checked what the instructions actually did. We used real hardware and real Host and client accounts. I will show how we built that evidence, and how you can review it beside the docs.

**Review links:** [Open CON-1187](https://vastai.atlassian.net/browse/CON-1187) · [Open the reviewer](http://127.0.0.1:4000/host/hosting-overview)

## 2. Get the pull request onto your computer

**On screen:** Copy the setup commands below the video. Fetch the PR head before reviewing.

**Spoken script**

Start by running the unmerged pull request on your computer. You need Git and Node version twenty four, with its package manager. Copy these commands from the setup page below the video. They download the docs, check out the latest published version of pull request one eighty five, and install its dependencies.

**Review links:** [Copy the setup commands](reviewer-setup.html#checkout) · [Open PR #185](https://github.com/vast-ai/docs/pull/185)

## 3. Start the docs, then the review overlay

**On screen:** Keep both terminals running. Review the Host pages on port 4000.

**Spoken script**

Keep two terminals open in that folder. Start the docs in terminal one. Then start the review server in terminal two. Open the Host overview on port four thousand. Port three thousand is the plain docs preview. To open this presentation, click Review presentation in the review panel. The video, setup commands, and Owner questions are included in your pull request checkout.

**Review links:** [Copy server commands](reviewer-setup.html#start) · [Open the review overlay](http://127.0.0.1:4000/host/hosting-overview) · [Review presentation](http://127.0.0.1:4000/__review__/presentation/)

## 4. Check what the account actually shows

**On screen:** Compare the documented route and labels with the signed-in Console.

**Spoken script**

Some claims needed an account check. We opened the real Console and checked individual, owner-team, and manager-team contexts. For notifications, we found that the documented address and section name needed a correction. We updated the docs to match the Settings page. We saved a record of what we saw, without personal account details. We did not change any notification settings.

**Review links:** [Open the UI claim](http://127.0.0.1:4000/host/notifications#where-to-find-notification-settings) · [Account evidence notes](runtime-account-evidence.md) · [Open the saved Console observation](http://127.0.0.1:4000/__review__/current-artifact?ref=verification%2Fevidence%2F2026-09-15-host-continuation-88-attempt-01%2Fd-console%2Fobservations.json&page=%2Fhost%2Fnotifications&claim=CUR-c8657007c73f9603&basis=0)

**Evidence scope, not spoken:** The observations cover the inspected contexts. They do not test message delivery or establish a universal role-permission rule.

## 5. Run the command written in the docs

**On screen:** Keep the command, CLI version, output and exit code.

**Spoken script**

For a command example, we ran the documented offer search through the Vast command line. We used a real client account. The command completed successfully and returned eight offers. We saved the exact command, software version, output, and exit code. This was a real command run. It checked the search example, without creating another rental.

**Review links:** [Open the CLI example](http://127.0.0.1:4000/host/not-in-search#comparing-your-ranking) · [CLI execution details](runtime-account-evidence.md) · [Open the retained CLI output review](http://127.0.0.1:4000/__review__/current-artifact?ref=verification%2Fevidence%2F2026-09-14-host-unvalidated-evidence-attempt-02%2Foffer-search-current-review.json&page=%2Fhost%2Fnot-in-search&claim=MCL-c36fc6f15087d072&basis=10)

**Evidence scope, not spoken:** 14 September 2026 · macOS / Python 3.12.12 · CLI 1c6f8b61. This search was separate from the H100 rental.

## 6. Check a real Host after installation

**On screen:** Review → After Install → Services report active → Show on page.

**Spoken script**

The first hardware example used a server with four H100 GPUs. We ran an approved modified installer over SSH. We then checked the services, the GPUs, and the storage separately. Here, Show on page connects the services result to the exact checklist sentence. The evidence supports that sentence on this tested host.

**Review links:** [Open After Install](http://127.0.0.1:4000/host/installing-host-software#after-install) · [Open the service result](http://127.0.0.1:4000/__review__/current-artifact?ref=verification%2Fevidence%2F2026-09-09-h100x4-direct-install-attempt-02%2Fpostcheck-02.json&page=%2Fhost%2Finstalling-host-software&claim=MCL-82fa8860fe3ef124&postcheck=POST-01) · [Open CON-1077](https://vastai.atlassian.net/browse/CON-1077)

**Evidence scope, not spoken:** Modified direct installation on 9 September. This is separate from testing the standard installer wizard or persistence after reboot.

## 7. The proof includes the result

**On screen:** Open View service-status result. Read the actual systemctl command and its four active results.

**Spoken script**

Open the saved service result. It shows the command we ran, a successful exit code, and four active services. Other saved checks show four GPUs, the Docker filesystem, and project quotas enabled. We kept the target, time, source version, and output with each result. This gives the reviewer something concrete to inspect. A successful service check does not prove that every installation step passed.

**Review links:** [Open this exact result](http://127.0.0.1:4000/__review__/current-artifact?ref=verification%2Fevidence%2F2026-09-09-h100x4-direct-install-attempt-02%2Fpostcheck-02.json&page=%2Fhost%2Finstalling-host-software&claim=MCL-82fa8860fe3ef124&postcheck=POST-01) · [Open the related checklist](http://127.0.0.1:4000/host/installing-host-software#after-install)

## 8. Follow the Host and client sides

**On screen:** Check the listing, create response, and independent client readback.

**Spoken script**

The next example follows a machine from the Host side to the client side. We used separate authenticated accounts. We listed the machine, read its settings back, found an offer, and created a client instance. The saved responses connect the listing and the instance to the same machine. This rental check used direct API requests. The command-line search we just saw was a separate test.

**Review links:** [Open Test Like a Client](http://127.0.0.1:4000/host/first-24-hours#test-like-a-client) · [Open CON-1584](https://vastai.atlassian.net/browse/CON-1584) · [Full rental evidence chain](runtime-account-evidence.md) · [Open the independent client readback](http://127.0.0.1:4000/__review__/current-artifact?ref=verification%2Fevidence%2F2026-09-09-h100x4-listing-rental-attempt-02%2Frental-run-03%2Finstance-read-03.json&page=%2Fhost%2Ffirst-24-hours&claim=MCL-92edb99129fc96c9)

**Evidence scope, not spoken:** 9 September 2026 · one H100 rented from the four-H100 host. API request source pinned to CLI 18c4f2c; the adjacent CLI/Jupyter command was not executed by this run.

## 9. Prove the instance worked, then clean up

**On screen:** Follow the retained run to its GPU result and independent cleanup checks.

**Spoken script**

We also ran a small calculation on the rented H100. The recorded result confirms that CUDA was available and the calculation returned the expected value. We then destroyed the instance. A separate read and the client instance list confirmed that it was gone. We saved those cleanup results too. This proves a small real rental workflow. It is not a full stress test.

**Review links:** [Open the rental page](http://127.0.0.1:4000/host/first-24-hours#test-like-a-client) · [Inspect all recorded steps](runtime-account-evidence.md) · [Open the GPU calculation result](http://127.0.0.1:4000/__review__/current-artifact?ref=verification%2Fevidence%2F2026-09-09-h100x4-listing-rental-attempt-02%2Frental-run-03%2Fgpu-result-01.json&page=%2Fhost%2Ffirst-24-hours&claim=MCL-e6fb82f7e167fdc8) · [Open cleanup for the same rental](http://127.0.0.1:4000/__review__/current-artifact?ref=verification%2Fevidence%2F2026-09-09-h100x4-listing-rental-attempt-02%2Frental-run-03%2Fcleanup-main.json)

**Evidence scope, not spoken:** The GPU result is bound to MCL-e6fb82f7e167fdc8. Cleanup is the original rental’s retained historical artifact; it is not the cleanup of a later test.

## 10. A real run found a docs problem

**On screen:** The Host saw four GPUs. The original Docker command failed with exit code 125.

**Spoken script**

The third example found a real problem in a documented diagnostic command. The host had four RTX six thousand Ada GPUs. The host could see them, but the Docker command in the draft failed. The error asked for the NVIDIA runtime option. We kept that failed result. It explains why the documentation needed a change.

**Review links:** [Open the original failure](http://127.0.0.1:4000/__review__/evidence?ref=verification%2Fevidence%2F2026-09-02-host-gpu-injection-attempt-01%2Fresult.md&binding=CLM-2113f9109b2c79c5) · [Open CON-1531](https://vastai.atlassian.net/browse/CON-1531)

**Evidence scope, not spoken:** This is the original failed run from 2 September. It is not the status of the corrected command.

## 11. Run the corrected command again

**On screen:** The published command used --runtime=nvidia. It saw all four GPUs and left no running test container.

**Spoken script**

We tested the NVIDIA runtime option, updated the docs, and ran the exact new command again. This time the container saw the same four GPUs as the host. We also checked that no test container was left running. The old failure and the successful retest remain separate records. The reviewer can trace the correction back to what actually happened on the machine.

**Review links:** [Open the corrected docs](http://127.0.0.1:4000/host/machine-errors#nvidia-container-runtime) · [Open the published-command retest](http://127.0.0.1:4000/__review__/current-artifact?ref=verification%2Fevidence%2F2026-09-02-host-gpu-injection-attempt-03%2Fresult.md&page=%2Fhost%2Fmachine-errors&claim=MCL-131308f1f480a9de)

**Evidence scope, not spoken:** This confirms the tested diagnostic command on that host. It does not mean that we reproduced or repaired every hardware fault.

## 12. Review the claim, its proof, and the remaining question

**On screen:** Open Review. Find the passage. Show it on the page. Open the result. Comment on exact wording.

**Spoken script**

To review this work, open the docs on port four thousand and click Review. Choose the relevant section. Show on page highlights the sentence being checked. Open its saved result and read the command, output, and limits. If something is wrong or unclear, select the wording and add a comment. Enter your name and explain the change needed. Feedback saves locally and can be exported for Jira. To find these hardware test records, click Evidence on GitHub on the presentation page. It opens the verification and evidence folders for pull request one eighty five. Click Owner questions on the same page for decisions that still need an answer. Use that page to see the question, the affected docs, and who needs to answer it.

**Review links:** [Try the reviewer](http://127.0.0.1:4000/host/machine-errors#nvidia-container-runtime) · [Evidence on GitHub](https://github.com/jjziets/docs/tree/646e94e5386aa0e45034c7de339eac275ac2232f/verification/evidence) · [Owner questions](owner-questions.html)

**Evidence scope, not spoken:** This capture selects text only. No demonstration feedback was submitted. Local notes and exports do not post to Jira automatically. GitHub contains the three retained hardware runs at snapshot 646e94e5. The presentation and Owner questions are included with the PR checkout.
