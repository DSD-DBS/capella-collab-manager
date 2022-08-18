import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { Router } from '@angular/router';
import { DeleteProjectDialogComponent } from 'src/app/projects/delete-project/delete-project-dialog/delete-project-dialog.component';
import {
  Project,
  ProjectService,
} from 'src/app/services/project/project.service';

@Component({
  selector: 'app-staged-projects-overview',
  templateUrl: './staged-projects-overview.component.html',
  styleUrls: ['./staged-projects-overview.component.css'],
})
export class StagedProjectsOverviewComponent implements OnInit {
  stagedProjects: Array<Project> = [];

  constructor(
    private projectService: ProjectService,
    private dialog: MatDialog,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.projectService.list().subscribe((projects: Array<Project>) => {
      this.stagedProjects = projects.filter((project) => project.staged_by);
    });
  }

  openDeleteDialog(project_name: string) {
    const deleteProjectDialog = this.dialog.open(DeleteProjectDialogComponent, {
      data: { project_name: project_name, overview: true },
    });
    deleteProjectDialog.afterClosed().subscribe((response) => {
      if (response) {
        this.projectService.deleteProject(project_name).subscribe({
          complete: () => this.router.navigateByUrl('/settings/requests'),
        });
      }
    });
  }
}
