// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { ProjectService } from 'src/app/services/repository/repository.service';

@Component({
  selector: 'app-create-repository',
  templateUrl: './create-repository.component.html',
  styleUrls: ['./create-repository.component.css'],
})
export class CreateRepositoryComponent implements OnInit {
  createRepositoryForm = new FormGroup({
    name: new FormControl('', Validators.required),
  });

  get name(): FormControl {
    return this.createRepositoryForm.get('name') as FormControl;
  }

  constructor(private projectService: ProjectService, private router: Router) {}

  ngOnInit(): void {}

  createRepository(): void {
    if (this.createRepositoryForm.valid) {
      this.projectService.createRepository(this.name.value).subscribe(() => {
        this.projectService.refreshRepositories();
        this.router.navigateByUrl('/settings');
      });
    }
  }
}
