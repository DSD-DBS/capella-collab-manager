/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Input } from '@angular/core';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-api-documentation',
  templateUrl: './api-documentation.component.html',
})
export class ApiDocumentationComponent {
  @Input() tag: string = '';
  @Input() hyperlink: string = '';

  getAPIDocsLink() {
    return `${environment.api_docs_url}/redoc#tag/${this.tag}/operation/${this.hyperlink}`;
  }
}
