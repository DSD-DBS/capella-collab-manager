/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { Component, Input } from '@angular/core';
import { MatIcon } from '@angular/material/icon';
import { API_DOCS_URL } from 'src/app/environment';

@Component({
  selector: 'app-api-documentation',
  templateUrl: './api-documentation.component.html',
  imports: [MatIcon],
})
export class ApiDocumentationComponent {
  @Input() tag = '';
  @Input() hyperlink = '';

  getAPIDocsLink() {
    return `${API_DOCS_URL}/redoc#tag/${this.tag}/operation/${this.hyperlink}`;
  }
}
