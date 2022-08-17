/*
 * SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { Component, Input, OnInit } from '@angular/core';

@Component({
  selector: 'app-model-source',
  templateUrl: './model-source.component.html',
  styleUrls: ['./model-source.component.css'],
})
export class ModelSourceComponent implements OnInit {
  constructor() {}

  @Input()
  repository = '';

  ngOnInit(): void {}
}
