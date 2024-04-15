<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Pull Request Acceptance Criteria

To reduce the burden on our maintainers, all PRs must meet the following
criteria before we start the review process. If the acceptance criteria are not
met, please mark the PR as a draft.

- All Github Action pipelines have to be green. If in individual cases the
  pipeline cannot be fixed independently or the pipeline failure is unrelated
  to the PR, then this should be justified in a comment in the pull request.
- The adapted code was sensibly covered with tests. CodeCov will indicate the
  test coverage with a comment.
- New features must be documented in the user documentation. If changes are
  made to existing functionality, the existing documentation must be adapted.
- Frontend changes must always be mobile optimized / responsive. You can find
  the requirements [here](./frontend/responsive-design/mobile-view.md).
- Migration scripts must also be written for changes to database models. They
  can be auto-generated, more information can be found
  [here](./backend/database-migration.md).
- The PR and commit descriptions describe the changes in a comprehensible way.
  Breaking changes must be marked as such. Commit messages have to follow the
  [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/#specification)
  specification.
- If there are conflicts with the main branch, they must be resolved.
- The frontend code must follow our
  [frontend code style guide](./frontend/code-style.md).
- The backend code must follow our
  [backend code style guide](./backend/code-style.md).
- Make sure that all raised exceptions use our
  [custom exception classes](./backend/exception.md), which can be resolved by
  the frontend.
- For each changed or added component in the frontend, a storybook story must
  be created. You can find more information [here](./frontend/storybook.md).

Once all acceptance criteria are met, you can mark the PR as ready for review
and a maintainer will review it.
