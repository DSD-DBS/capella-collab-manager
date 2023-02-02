<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

Please note the following limitations:

- To setup the diagram cache, you'll need a Git instance of type Gitlab. Other
  instances are not supported.
- You need a pipeline in the Git repository of the model, which serves the
  diagrams via
  [job artifacts](https://docs.gitlab.com/ee/ci/pipelines/job_artifacts.html).
  You can use our Gitlab CI pipeline template: In progress. The job has to be
  called `update_capella_diagram_cache`.
- Your pipeline should not contain more than 20 jobs.

## Define a API URL for the Git instance

## Add the diagram cache to the Gitlab CI

## View the diagrams
