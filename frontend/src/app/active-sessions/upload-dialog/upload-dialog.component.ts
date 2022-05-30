import { Component, OnInit, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Subscription } from 'rxjs';
import { Session } from 'src/app/schemes';
import { LoadFilesService } from 'src/app/services/load-files/load-files.service';

@Component({
  selector: 'upload-dialog',
  templateUrl: "upload-dialog.component.html",
  styleUrls: ["upload-dialog.component.css"]
})
export class UploadDialogComponent implements OnInit{

  files: Array<File> = []
  private subscription: Subscription | undefined

  uploadProgress: number | null = null;

  constructor(
    private loadService: LoadFilesService,
    public dialogRef: MatDialogRef<UploadDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public session: Session
  ) {}

  ngOnInit(): void {}

  onFileInput(files: FileList | null): void {
    if (files) {
      for (let file of Array.from(files)) {
        this.files.push(file);
      }
    }
  }

  onSubmit() {
    const formData = new FormData();
    /*this.files.forEach(file => {
      formData.append('files[]', file, this.files[0].name);
    })*/
    formData.append('file', this.files[0], this.files[0].name)

    if (this.files) {
      this.subscription = this.loadService.upload(this.session.id, formData).subscribe()
    }
  }

  ngOnDestroy() {
    this.subscription?.unsubscribe()
  }
}