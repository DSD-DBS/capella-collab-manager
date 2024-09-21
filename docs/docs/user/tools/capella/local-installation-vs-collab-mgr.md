<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Difference between a local installation and the Capella Collaboration Manager

You may have thought about why you should use the Capella Collaboration Manager
and not just a local Capella installation. It depends on a variety of factors,
so here is a decision help:

<table markdown="span">
  <tr>
    <th style="width:20%"></th>
    <th style="width:40%">Local Capella Installation</th>
    <th style="width:40%">Capella Collaboration Manager</th>
  </tr>
  <tr>
    <td><b>Differences between operating systems</b></td>
    <td>When the team uses different operating systems or dependencies, there may be small differences in the Capella behaviour. Bugs have to be collected and reported for each OS individully. In addition, it's important that all users use the same font, otherwise diagrams will change on each save when a new font is applied. Diagrams might look different on different devices.</td>
    <td>All sessions run on Linux in a Docker container with exactly the same dependencies. Bugs are easier to reproduce.</td>
  </tr>
  <tr>
    <td><b>Configuration</b></td>
    <td>Manual configuration by users. Some configuration options have to be aligned in the team.</td>
    <td>Pre-defined configuration according to best-practises and experience. Users may deviate from the central configuration via modifications in their personal workspace.</td>
  </tr>
  <tr>
    <td><b>Performance</b></td>
    <td>Native Capella performance, no latency in local projects.</td>
    <td>Performance depends on the internet connection and latency.</td>
  </tr>
  <tr>
    <td><b>Backups</b></td>
    <td>Unless saved on a remote server like TeamForCapella or Git, changes have to be backed up manually.</td>
    <td>Workspaces can be backed up regularly (this service might not be enabled for all environments).</td>
  </tr>
  <tr>
    <td><b>Offline working</b></td>
    <td>Offline working possible with local models or with the Git workflow. Not possible with TeamForCapella.</td>
    <td>Access via browser with active internet connection. Working offline is not possible at the moment.</td>
  </tr>
  <tr>
    <td><b>Installation effort</b></td>
    <td>Software, plugins, dependencies and dropins have to be installed and updated manually.</td>
    <td>Everything is installed centrally and managed by the System Administrators.</td>
  </tr>
  <tr>
    <td><b>Working together in one Capella instance</b></td>
    <td>Requires external software for screen sharing.</td>
    <td>Natively integrated with session sharing. You can see other users' pointers and collaborate interactively.</td>
  </tr>
  <tr markdown="span">
    <td><b>Task automation</b></td>
    <td>Tasks can be automated using `capellambse` and `capellambse-context-diagrams` locally. Python, dependencies and packages have to be installed manually.</td>
    <td>Native integration of Jupyter with the latest versions of `capellambse` and `capellambse-context-diagrams` preinstalled.</td>
  </tr>
  <tr>
    <td><b>Support effort</b></td>
    <td>High effort to support installation on many different devices. Workspaces and logs are not accessible centrally.</td>
    <td>Central log collection and installation. For debug purposes, workspace can be accessed by System Administrators.</td>
  </tr>
  <tr>
    <td><b>Access management</b></td>
    <td>Access has to be managed centrally, either manually on the TeamForCapella server or via AD groups.</td>
    <td>Access is self-managed by project administrators.</td>
  </tr>
  <tr>
    <td><b>Support for read-only sessions</b></td>
    <td>Users consume licenses in TeamForCapella projects for read-access. Changes to the model are not prohibited.</td>
    <td>All changes to models in read-only sessions are discarded. No license is needed for read-only sessions.</td>
  </tr>
  <tr>
    <td><b>Monitoring capabilities</b></td>
    <td>Monitoring has to be built manually.</td>
    <td>Monitoring of TeamForCapella repositories, license usage and usage of different tools / versions.</td>
  </tr>
</table>
