<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Frontend Testing

## Integration testing

### Technologies

- We use [Jasmine](https://jasmine.github.io) as testing framework
- [Karma](https://karma-runner.github.io) is used as test runner
- We use [istanbul](https://istanbul.js.org/) to measure and visualize the code coverage

### Additional sources

- [Official angular testing guide](https://angular.io/guide/testing)
- Recommended: [Detailed angular testing guide](https://testing-angular.com/)

### General

#### Robust component tests

When testing components, we must query the elements needed for the test.
To ensure that even if the element type or attributes changes, the element
can still be queried, we assign a `data-testId` to each needed element.
This not only increases robustness, but also makes it very easy
to query elements. The value assigned to the test id should clearly describe
the usage of the element and should not be too long.
For example, one can use the schema `data-testId=<type>-<description>`
where the prefix usually describes the general contex (e.g., whether it is
an input, button, textfield, etc.) and the following description specifies the
usage of it (e.g., createProject).

#### Element helper functions

Usually testing components consists of querying elements, applying changes
to them, triggering events on them, and then comparing the results with the
expected results. To reduce repetition and increase readability, one should
use existing helper functions or create new ones if none exist.

### Executing tests

To execute the integration tests, one needs to run `make test`. However, in some
cases it is not possible to correctly set the `CHROME_BIN` that is needed to generate
the test output inside the browser. If this is the case, one should either set
the `CHORME_BIN` in the make file or simply run `EXPORT CHROME_BIN=<path>`
followed by `ng test`. Beyond that, it is not necessary to run anything else
(e.g., the backend) for test execution.

#### Output

The resulting output in the browser considers three different cases:

1. Green tests are _successful_ tests
2. Yellow tests (marked with a ☆) are _deactivated_ tests
3. Red tests are _failed_ tests

The general code coverage statistics (i.e. statement, branch, function,
and line coverage) are output to the console. To also see what exactly is
covered and what is missing, one can open the `index.html` file in the
`/frontend/test-results/istanbul-coverage` folder.

## End-to-End testing

### Technologies

- We use [playwright](https://playwright.dev) for E2E testing

### Test generation

Playwright supports the generation of E2E tests by interacting
with the frontend and recording each action and input. This can be started
by executing `npx playwright codegen localhost:4200` but needs a running
frontend and backend to work.

Test generation can significantly speed up test creation, but in general
one should only use the resulting test as a base and adjust it accordingly.
For example, check selectors and adjust them to make them more robust,
or add more expectations as needed.

### Executing tests

To run the E2E tests, one must first make sure that a backend is running.
If that is the case, one can run `npx playwright test` to start
the tests. In case of an error the browser will be directly opened and
show the last test report, otherwise one can open it with `npx playwright show-report`.
A very helpful option when running the tests is `--trace on`. This provides,
for example, a screenshot of the action and the before/after state (for each step),
contains a detailed log, and one can also view the console output and
network calls performed.
