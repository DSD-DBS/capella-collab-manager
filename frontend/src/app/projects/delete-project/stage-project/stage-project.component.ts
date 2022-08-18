import { Component, Input, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { Router } from '@angular/router';
import { StageProjectDialogComponent } from 'src/app/projects/delete-project/stage-project-dialog/stage-project-dialog.component';
import { ProjectService } from 'src/app/services/project/project.service';
@Component({
  selector: 'app-stage-project',
  templateUrl: './stage-project.component.html',
  styleUrls: ['./stage-project.component.css'],
})
export class StageProjectComponent implements OnInit {
  @Input()
  project_name: string = '';

  constructor(
    private dialog: MatDialog,
    private projectService: ProjectService,
    private router: Router
  ) {}
  ngOnInit(): void {}

  openStageDialog() {
    const stageProjectDialog = this.dialog.open(StageProjectDialogComponent, {
      data: this.project_name,
    });
    stageProjectDialog.afterClosed().subscribe((response) => {
      if (response) {
        this.projectService
          .stageForProjectDeletion(this.project_name)
          .subscribe(() => this.router.navigateByUrl('/projects'));
      }
    });
  }
}
