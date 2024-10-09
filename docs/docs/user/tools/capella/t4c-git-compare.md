<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Ways of Co-working on a Capella Project

## Quick Comparison

<table markdown="span">
  <tr>
    <th></th>
    <th>Git</th>
    <th>TeamForCapella</th>
  </tr>
  <tr>
    <td><b>Multiple workstreams</b></td>
    <td>Different workstreams available via branches</td>
    <td>Not recommended, only possible via different repositories</td>
  </tr>
  <tr>
    <td><b>Concurrent working</b></td>
    <td>Very challenging because of merge conflict potential, a possible workflow is described [here](./git/index.md).</td>
    <td>Is possible. Diagrams are locked, no risk of merge conflicts.</td>
  </tr>
  <tr>
    <td><b>Merge conflicts</b></td>
    <td>Resolution of merge conflicts can be challenging.</td>
    <td>No merge conflicts when one workstream is used. For multiple workstreams, the resolution of merge conflicts can be challenging.</td>
  </tr>
  <tr markdown="span">
    <td><b>License</b></td>
    <td>No license needed[^1]</td>
    <td>TeamForCapella license required[^2]</td>
  </tr>
  <tr markdown="span">
    <td><b>Complexity</b></td>
    <td>Git knowledge is required[^3]</td>
    <td>Easy to use</td>
  </tr>
  <tr>
    <td><b>Stability</b></td>
    <td>Very stable solution as changes are initially saved locally. Temporary server downtimes can also be bridged.</td>
    <td>Changes may be lost if the server becomes unavailable during work.</td>
  </tr>
  <tr>
    <td><b>Potential of data loss</b></td>
    <td>Changes are backed up after each push (more regularly).</td>
    <td>Changes are backed up on a nightly basis.</td>
  </tr>
  <tr>
    <td><b>Automation</b></td>
    <td>Possible via CI/CD in the Git repository.</td>
    <td>Possible via TeamForCapella &rarr; Git synchronisation (runs on a nightly basis).</td>
  </tr>
  <tr markdown="span">
    <td><b>Change control</b></td>
    <td>Reviews are possible via merge requests[^4]</td>
    <td>Change control is nearly impossible, no barriers.</td>
  </tr>
  <tr>
    <td><b>Release tagging</b></td>
    <td>Directly possible via tags in Git.</td>
    <td>Possible via TeamForCapella &rarr; Git synchronisation (Releases are stored as tags in the Git repository).</td>
  </tr>
</table>

[^1]:
    You can use any standardized Git server. Depending on the server used,
    licenses for the Git server may be required.

[^2]:
    You need a valid TeamForCapella license and TeamForCapella server installed
    and integrated in the Collaboration Manager.

[^3]:
    For the basic workflow, a simple Git knowledge that includes commit, pull
    and push is sufficient. However, it is necessary to have at least one Git
    expert in the project to deal with potential merge conflicts and unexpected
    situations.

[^4]:
    To review changes, the Eclipse EMF diff/merge tool can be used. However, in
    practice this proves to be too time-consuming, as many changes become
    confusing very quickly.

## Some General Words

-   **Git-only** - the modeling team uses a git repository to work on the
    model. The team may use git branches to work on features or capabilities in
    parallel and a main branch is used for integration and release-tagging.
    This way of working gives the modeling leads / change control board great
    control over what contents make it to the model that is used for releases
    (of things like design documentation). On the downside this co-working
    method is fairly complicated and requires skilled modeling leadership for
    challenges like merge conflict resolution and fragmentation management (a
    way to break up model into smaller files to reduce density of merge
    conflicts).
-   **Git + TeamForCapella** - with this approach the modeling team can co-work
    with a very high degree of concurrency and stay away from the difficulties
    of merge conflict resolution. On the downside it is much harder to control
    what makes it into the model as there is no barrier except for maybe a
    modeling process that would stop a person from making changes that are not
    allowed. Yet there are a few ways around that limitation. For teams with
    basic or no experience in modeling and git this is probably the best way to
    start co-woking. Git is still used for nightly backup of the model and
    release-tagging.

    !!! info "TeamForCapella license required"

        For this co-working method to be enabled you need a valid
        TeamForCapella license and TeamForCapella server installed and
        integrated with Collab-Manager.
