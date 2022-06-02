import { Component, OnInit, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Subscription, finalize } from 'rxjs';
import { Session } from 'src/app/schemes';
import { LoadFilesService } from 'src/app/services/load-files/load-files.service';
import { HttpEventType } from '@angular/common/http'

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
        if (! this.files.includes(file)){
          this.files.push(file);
        }
      }
    }
  }

  removeFile(file: File): void {
    const index: number = this.files.indexOf(file);
    this.files.splice(index, 1);
  }

  onSubmit() {
    const formData = new FormData();
    this.files.forEach(file => {
      formData.append('files', file, file.name);
    })
    formData.append('id', this.session.id)

    const upload$ = this.loadService.upload(this.session.id, formData).pipe(
      finalize(() => this.reset())
    );

    this.subscription = upload$.subscribe(event => {
      if (event && event.type == HttpEventType.UploadProgress) {
        this.uploadProgress = Math.round(100 * (event.loaded / event.total));
      }
    })
  }

  cancelUpload() {
    this.subscription?.unsubscribe()
    this.reset();
  }

  reset() {
    this.uploadProgress = null;
    this.subscription = undefined;
    this.files = [];
  }
}