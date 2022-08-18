import { Component, Inject, OnInit } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { DeleteProjectComponent } from 'src/app/projects/delete-project/delete-project.component';

@Component({
  selector: 'app-delete-project-dialog',
  templateUrl: './delete-project-dialog.component.html',
  styleUrls: ['./delete-project-dialog.component.css'],
})
export class DeleteProjectDialogComponent implements OnInit {
  constructor(
    public dialogRef: MatDialogRef<DeleteProjectComponent>,
    @Inject(MAT_DIALOG_DATA) public project_name: string
  ) {}
  ngOnInit(): void {}
}
