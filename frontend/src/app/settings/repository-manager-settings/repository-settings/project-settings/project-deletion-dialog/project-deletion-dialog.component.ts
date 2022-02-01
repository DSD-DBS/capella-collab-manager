import { Component, Inject, OnInit } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import {
  RepositoryProject,
  RepositoryProjectService,
} from 'src/app/services/repository-project/repository-project.service';

@Component({
  selector: 'app-project-deletion-dialog',
  templateUrl: './project-deletion-dialog.component.html',
  styleUrls: ['./project-deletion-dialog.component.css'],
})
export class ProjectDeletionDialogComponent implements OnInit {
  constructor(
    private projectService: RepositoryProjectService,
    public dialogRef: MatDialogRef<ProjectDeletionDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public project: RepositoryProject
  ) {}

  ngOnInit(): void {}

  removeProject(): void {
    this.projectService
      .deleteRepositoryProject(this.project.repository_name, this.project.id)
      .subscribe(() => {
        this.dialogRef.close(true);
      });
  }
}
