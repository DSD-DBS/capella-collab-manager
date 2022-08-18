import { Component, Input, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { Router } from '@angular/router';
import { DeleteProjectDialogComponent } from 'src/app/projects/delete-project/delete-project-dialog/delete-project-dialog.component';
import { ProjectService } from 'src/app/services/project/project.service';
@Component({
  selector: 'app-delete-project',
  templateUrl: './delete-project.component.html',
  styleUrls: ['./delete-project.component.css'],
})
export class DeleteProjectComponent implements OnInit {
  @Input()
  project_name: string = '';

  constructor(
    private dialog: MatDialog,
    private projectService: ProjectService,
    private router: Router
  ) {}

  ngOnInit(): void {}

  openDeleteDialog() {
    const deleteProjectDialog = this.dialog.open(DeleteProjectDialogComponent, {
      data: { project_name: this.project_name, overview: false },
    });
    deleteProjectDialog.afterClosed().subscribe((response) => {
      if (response) {
        this.projectService.deleteProject(this.project_name).subscribe({
          complete: () => this.router.navigateByUrl('/projects'),
        });
      }
    });
  }
}
