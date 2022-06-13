// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { NestedTreeControl, FlatTreeControl } from '@angular/cdk/tree';
import { Component, OnInit, Inject, OnDestroy } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatDialog } from '@angular/material/dialog';

import { Subscription, finalize, BehaviorSubject } from 'rxjs';
import { Session } from 'src/app/schemes';
import {
  FileTree,
  LoadFilesService,
} from 'src/app/services/load-files/load-files.service';
import { HttpEventType } from '@angular/common/http';

import { FileExistsDialogComponent } from './file-exists-dialog/file-exists-dialog.component';

@Component({
  selector: 'upload-dialog',
  templateUrl: 'upload-dialog.component.html',
  styleUrls: ['upload-dialog.component.css'],
})
export class UploadDialogComponent implements OnInit, OnDestroy {
  files: [File, string][] = [];
  private subscription: Subscription | undefined;
  uploadProgress: number | null = null;
  loadingFiles = false;

  treeControl = new NestedTreeControl<FileTree>((node) => node.children);
  dataSource = new BehaviorSubject<FileTree[]>([]);

  lastID: number = 0;

  constructor(
    private loadService: LoadFilesService,
    private dialog: MatDialog,
    public dialogRef: MatDialogRef<UploadDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public session: Session
  ) {}

  ngOnInit(): void {
    this.loadService.getCurrentFiles(this.session.id).subscribe({
      next: (file: FileTree) => {
        this.dataSource.next([file]);
      },
      complete: () => {
        this.loadingFiles = false;
      },
    });
  }

  ngOnDestroy(): void {
    this.subscription?.unsubscribe();
  }

  hasChild = (_: number, node: FileTree) => !!node.children;

  isExpandable = (node: FileTree): boolean => !!node.children;

  addFiles(files: FileList | null, path: string, parentNode: FileTree): void {
    if (files) {
      for (let file of Array.from(files)) {
        if (this.checkIfFileExists(file, path)) {
          const dialogRef = this.dialog.open(FileExistsDialogComponent, {
            data: file.name,
          });
          dialogRef.afterClosed().subscribe((response) => {
            if (!this.files.includes([file, path]) && response) {
              this.files.push([file, path]);
            }
          });
        } else if (!this.files.includes([file, path])) {
          console.log(parentNode);
          console.log(this.dataSource.value);
          parentNode.children?.push({
            path: path,
            name: file.name,
            type: 'file',
            children: null,
            newFile: true,
          });
          this.dataSource.next([{ ...parentNode }]);
          this.files.push([file, path]);
        }
      }
    }
  }

  checkIfFileExists(file: File, prefix: string): boolean {
    var result = false;
    this.dataSource.value[0].children?.forEach((child: FileTree) => {
      if (file.name == child.name) result = true;
    });
    return result;
  }

  removeFileFromSelection(file: File, prefix: string): void {
    const index: number = this.files.indexOf([file, prefix]);
    this.files.splice(index, 1);
  }

  onSubmit() {
    const formData = new FormData();
    this.files.forEach(([file, prefix]: [File, string]) => {
      console.log(file, prefix, prefix + `/${file.name}`);
      formData.append('files', file, prefix + `/${file.name}`);
    });
    formData.append('id', this.session.id);

    const upload$ = this.loadService
      .upload(this.session.id, formData)
      .pipe(finalize(() => this.reset()));

    this.subscription = upload$.subscribe((event) => {
      if (event && event.type == HttpEventType.UploadProgress) {
        this.uploadProgress = Math.round(100 * (event.loaded / event.total));
      }
    });
  }

  cancelUpload() {
    this.subscription?.unsubscribe();
    this.reset();
  }

  reset() {
    this.uploadProgress = null;
    this.subscription = undefined;
    this.files = [];
    window.location.reload();
  }
}
