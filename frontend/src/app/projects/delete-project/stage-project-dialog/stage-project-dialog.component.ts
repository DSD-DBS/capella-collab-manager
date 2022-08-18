import { Component, Inject, OnInit } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { StageProjectComponent } from 'src/app/projects/delete-project/stage-project/stage-project.component';

@Component({
  selector: 'app-stage-project-dialog',
  templateUrl: './stage-project-dialog.component.html',
  styleUrls: ['./stage-project-dialog.component.css'],
})
export class StageProjectDialogComponent implements OnInit {
  constructor(
    public dialogRef: MatDialogRef<StageProjectComponent>,
    @Inject(MAT_DIALOG_DATA) public project_name: string
  ) {}
  ngOnInit(): void {}
}
