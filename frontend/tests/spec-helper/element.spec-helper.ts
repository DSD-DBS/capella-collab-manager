/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { DebugElement } from '@angular/core';
import { ComponentFixture } from '@angular/core/testing';
import { By } from '@angular/platform-browser';

export function findElByTestId<T>(
  fixture: ComponentFixture<T>,
  testId: string,
): DebugElement {
  return fixture.debugElement.query(By.css(`[data-testId="${testId}"]`));
}

export function findComponent<T>(
  fixture: ComponentFixture<T>,
  selector: string,
): DebugElement {
  return fixture.debugElement.query(By.css(selector));
}

export function click<T>(fixture: ComponentFixture<T>, testId: string): void {
  const element = findElByTestId(fixture, testId);
  const event = makeClickEvent(element.nativeElement);
  element.triggerEventHandler('click', event);
}

export function makeClickEvent(target: EventTarget): Partial<MouseEvent> {
  return {
    preventDefault(): void {},
    stopPropagation(): void {},
    stopImmediatePropagation(): void {},
    type: 'click',
    target,
    currentTarget: target,
    bubbles: true,
    cancelable: true,
    button: 0,
  };
}

export function expectText<T>(
  fixture: ComponentFixture<T>,
  testId: string,
  expectedText: string,
): void {
  const element = findElByTestId(fixture, testId);
  const actualText = element.nativeElement.text;
  expect(actualText).toBe(expectedText);
}

export function setFieldValue<T>(
  fixture: ComponentFixture<T>,
  testId: string,
  value: string,
): void {
  setElementValue(findElByTestId(fixture, testId).nativeElement, value);
}

export function setElementValue(
  element: HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement,
  value: string,
): void {
  element.value = value;
  const event = new Event('input', { bubbles: true, cancelable: false });
  element.dispatchEvent(event);
}
