# V2 PROGRESS.md — Living Changelog for CNN Upgrade

## Initialization
- Initialized isolated `v2/` working directory for the CNN architecture upgrade.
- Explicitly scoped the architectural inheritance: keeping base verified components (`systolic_array.v`, `mac_q7_8.v`, `relu_q7_8.v`, `layer_relu.v`) from V1.
- Staged development plan for new V2 components: convolutions, pooling, line buffers, and an expanded MLP head.
