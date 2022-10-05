/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { test, expect } from '@playwright/test';

const nearPixelArea = 50; // Specifies how far away an element can be when using near

test('test the full project creation workflow', async ({ page }) => {
  const testProjectName = `test-project-name-${Math.trunc(
    Math.random() * 1000
  )}`;
  const testProjectDescription = 'test-project-description';

  await page.goto('http://localhost:4200/');

  // Check whether you got redirected to the /auth page
  await expect(page).toHaveURL('http://localhost:4200/auth');

  await page.locator('button:text-matches("Login with .*", "g")').click();

  // Wait for the response from the backend
  await page.waitForResponse('http://localhost:8000/api/v1/authentication/');

  // Everything static except the state which is generated from the backend
  await expect(page).toHaveURL(
    /http:\/\/localhost:8083\/default\/authorize\?response_type=code&client_id=default&redirect_uri=http%3A%2F%2Flocalhost%3A4200%2Foauth2%2Fcallback&scope?=openid&state=.*&grant_type=authorization_code/
  );

  await page
    .locator('[placeholder="Enter any user\\/subject"]')
    .fill('username');
  await page.locator('input:has-text("Sign-in")').click();
  await expect(page).toHaveURL('http://localhost:4200/');

  await page.locator('a:has-text("Projects")').click();
  await expect(page).toHaveURL('http://localhost:4200/projects');

  await page.locator('a', { hasText: 'Add new project' }).click();
  await expect(page).toHaveURL('http://localhost:4200/projects/create');

  const genInfoMatStepHeaderLocator = page.locator('mat-step-header', {
    hasText: 'General information',
  });
  const addTeamMemMatStepHeaderLocator = page.locator('mat-step-header', {
    hasText: 'Add team members',
  });
  const addModelsMatStepHeaderLocator = page.locator('mat-step-header', {
    hasText: 'Add models',
  });

  await expect(genInfoMatStepHeaderLocator).toHaveAttribute(
    'aria-selected',
    'true'
  );
  await expect(addTeamMemMatStepHeaderLocator).toHaveAttribute(
    'aria-disabled',
    'true'
  );
  await expect(addModelsMatStepHeaderLocator).toHaveAttribute(
    'aria-disabled',
    'true'
  );

  await page
    .locator(`input:near(:text("Name"), ${nearPixelArea})`)
    .first()
    .fill(testProjectName);
  await page
    .locator(`textarea:near(:text("Description"), ${nearPixelArea})`)
    .first()
    .fill(testProjectDescription);
  await page.locator('button:has-text("Create Project")').click();

  await expect(genInfoMatStepHeaderLocator).toHaveAttribute(
    'aria-selected',
    'false'
  );
  await expect(addTeamMemMatStepHeaderLocator).toHaveAttribute(
    'aria-selected',
    'true'
  );
  await expect(addModelsMatStepHeaderLocator).toHaveAttribute(
    'aria-disabled',
    'true'
  );

  await page.locator('button', { hasText: 'Skip' }).click();

  await expect(genInfoMatStepHeaderLocator).toHaveAttribute(
    'aria-selected',
    'false'
  );
  await expect(addTeamMemMatStepHeaderLocator).toHaveAttribute(
    'aria-selected',
    'false'
  );
  await expect(addModelsMatStepHeaderLocator).toHaveAttribute(
    'aria-selected',
    'true'
  );

  await page
    .locator('a:has-text("Skip model creation and finish project creation")')
    .click();
  await expect(page).toHaveURL(
    `http://localhost:4200/project/${testProjectName}`
  );

  await page.locator('a:has-text("Projects")').click();
  await expect(page).toHaveURL('http://localhost:4200/projects');

  await expect(
    page.locator(`//a[@href='/project/${testProjectName}']`)
  ).toBeVisible();
});
