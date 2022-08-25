// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, OnInit } from '@angular/core';
import { BehaviorSubject, map } from 'rxjs';
import { NavBarService } from 'src/app/navbar/service/nav-bar.service';
import {
  Tool,
  ToolService,
  Type,
  Version,
} from 'src/app/services/tools/tool.service';

@Component({
  selector: 'app-dockerimage-settings',
  templateUrl: './dockerimage-settings.component.html',
  styleUrls: ['./dockerimage-settings.component.css'],
})
export class DockerimageSettingsComponent implements OnInit {
  constructor(
    private navbarService: NavBarService,
    private toolService: ToolService
  ) {}

  ngOnInit(): void {
    this.navbarService.title = 'Settings / Core / Dockerimages';
    this.toolService.get_tools().subscribe(this.toolService._tools);
    this.toolService.get_versions().subscribe(this.toolService._versions);
    this.toolService.get_types().subscribe(this.toolService._types);
  }
}
