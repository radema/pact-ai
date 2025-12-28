# Feature Request: feature-bolt-commands

**Status:** DRAFT

## Instructions

In this bolt we focus on the features below

1. Add 'req' as a valid target to 'pact seal'
2. Refactor `pact seal status` and `pact seal verify` so that the seal command is always related to a target and make separate command pact status (with option -b to specify the bolt name. For the moment is possible to check the status of only bolts). With a similar behaviour, we have the 'verify' command which by defult is on the current bolt but with '-b' can be applied to other bolts. The verify should verify the coherence of sha as today but also the temporal sequence of req >= specs >= plan >= mrp
3. add a switch context command such as pact checkout 'bolt-name' (to mimic git!)
4. add a delete command for a bolt. We assume that it is not possible to delete the current bolt.
5. imeplement a pact archive bolt. A bolt can be archived only when it is fully verified (from req to mrp). When archived, the bolt directory is fully moved to the .pacts/archive folder
