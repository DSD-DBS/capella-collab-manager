/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { NgClass } from '@angular/common';
import { HttpEventType } from '@angular/common/http';
import { Component, Inject, OnInit } from '@angular/core';
import { FormControl, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCheckbox } from '@angular/material/checkbox';
import { MatRippleModule } from '@angular/material/core';
import {
  MAT_DIALOG_DATA,
  MatDialog,
  MatDialogRef,
} from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBar } from '@angular/material/progress-bar';
import { MatTableDataSource } from '@angular/material/table';
import { MatTreeModule } from '@angular/material/tree';
import { saveAs } from 'file-saver';
import { ConfirmationDialogComponent } from 'src/app/helpers/confirmation-dialog/confirmation-dialog.component';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import { Session, SessionsService } from 'src/app/openapi';
import { PathNode } from 'src/app/sessions/service/session.service';

@Component({
  selector: 'app-file-browser-dialog',
  templateUrl: 'file-browser-dialog.component.html',
  imports: [
    FormsModule,
    MatButtonModule,
    MatCheckbox,
    MatIconModule,
    MatProgressBar,
    MatRippleModule,
    MatTreeModule,
    NgClass,
    ReactiveFormsModule,
  ],
})
export class FileBrowserDialogComponent implements OnInit {
  filesToUpload: [File, string][] = [];
  uploadProgress: number | null = null;
  loadingFiles = false;

  dataSource = new MatTableDataSource<PathNode>([]);

  childrenAccessor = (node: PathNode) => node.children ?? [];

  constructor(
    private sessionsService: SessionsService,
    private dialog: MatDialog,
    public dialogRef: MatDialogRef<FileBrowserDialogComponent>,
    private toastService: ToastService,
    @Inject(MAT_DIALOG_DATA) public session: SessionWithDownloadInformation,
  ) {}

  showHiddenFiles = new FormControl(false);

  ngOnInit(): void {
    this.loadFiles();
  }

  loadFiles(): void {
    this.loadingFiles = true;

    this.sessionsService
      .listFiles(this.session.id, this.showHiddenFiles.value as boolean)
      .subscribe({
        next: (file) => {
          const treeNode = file as PathNode;
          treeNode.isExpanded = true;
          this.dataSource.data = [treeNode];
        },
        error: () => {
          this.dialogRef.close();
        },
        complete: () => {
          this.loadingFiles = false;
        },
      });
  }

  hasChild = (_: number, node: PathNode) => !!node.children;

  addFiles(files: FileList | null, parentNode: PathNode): void {
    if (!files) return;
    for (const file of Array.from(files)) {
      const existingFile = this.checkIfFileExists(parentNode, file.name);
      if (existingFile) {
        if (existingFile.type === 'directory') {
          this.toastService.showError(
            "Can't overwrite directories",
            `A directory with the name '${file.name}' already exists in the workspace.`,
          );
          continue;
        }
        const fileExistsDialog = this.dialog.open(ConfirmationDialogComponent, {
          data: {
            title: 'Overwrite file in workspace',
            text: `Do you want to overwrite the file '${file.name}' in your workspace?`,
          },
        });
        fileExistsDialog.afterClosed().subscribe((response) => {
          if (
            !this.filesToUpload.includes([file, parentNode.path]) &&
            response
          ) {
            this.stageFile(parentNode, file);
          }
        });
      } else if (!this.filesToUpload.includes([file, parentNode.path])) {
        this.stageFile(parentNode, file);
      }
    }
  }

  stageFile(parentNode: PathNode, file: File) {
    this.addFileToTree(parentNode, file.name);
    this.filesToUpload.push([file, parentNode.path]);
  }

  addFileToTree(parentNode: PathNode, name: string): void {
    const existingFile = parentNode.children?.find(
      (child) => child.name === name,
    );

    parentNode.isExpanded = true;

    if (existingFile) {
      existingFile.isModified = true;
    } else {
      parentNode.children?.push({
        path: parentNode.path + `/${name}`,
        name,
        type: 'file',
        children: null,
        isNew: true,
      });

      // Trigger change detection
      this.dataSource.data = this.dataSource.data; // eslint-disable-line no-self-assign
    }
  }

  checkIfFileExists(parentNode: PathNode, fileName: string): PathNode | null {
    if (parentNode.children) {
      for (const child of parentNode.children) {
        if (fileName == child.name) return child;
      }
    }
    return null;
  }

  removeFile(node: PathNode): void {
    this.removeFileFromSelection(node.path, node.name);
    this.removeFileFromTree(node);
  }

  private _removeElementByPath(path: string): void {
    // Remove the element using path traversal

    const paths = path.split('/').slice(2);
    const filename = paths.pop();

    let currentNode = this.dataSource.data[0];
    for (const name of paths) {
      const child = currentNode.children?.find((child) => child.name === name);
      if (!child) return;
      currentNode = child;
    }
    if (!currentNode.children) return;
    const childIndex = currentNode.children.findIndex(
      (child) => child.name === filename,
    );
    if (childIndex === -1) return;
    currentNode.children?.splice(childIndex, 1);
  }

  removeFileFromTree(node: PathNode): void {
    if (node.isModified) {
      node.isModified = false;
    } else {
      this._removeElementByPath(node.path);
      // Trigger change detection
      this.dataSource.data = this.dataSource.data; // eslint-disable-line no-self-assign
    }
  }

  removeFileFromSelection(path: string, filename: string): void {
    const index = this.filesToUpload.findIndex(
      ([file, prefix]) => file.name === filename && prefix === path,
    );
    if (!index) return;
    this.filesToUpload.splice(index, 1);
  }

  submit() {
    let size = 0;
    this.filesToUpload.forEach(([file, _]: [File, string]) => {
      size += file.size;
    });

    if (size > 31457280) {
      this.toastService.showError(
        'File too large!',
        'The file size must not exceed 30MB!',
      );
      return;
    }

    const files = this.filesToUpload.map(
      ([file, prefix]) =>
        new File([file], `${prefix}/${file.name}`, {
          type: file.type,
          lastModified: file.lastModified,
        }),
    );
    this.sessionsService
      .uploadFiles(this.session.id, files, 'events', true)
      .subscribe({
        next: (event) => {
          if (event.type == HttpEventType.Response) {
            this.dialogRef.close();
            this.toastService.showSuccess(
              'Upload successful',
              `${files.length} file(s) uploaded successfully`,
            );
          } else if (
            event.type == HttpEventType.UploadProgress &&
            event.total
          ) {
            this.uploadProgress = Math.round(
              100 * (event.loaded / event.total),
            );
          }
        },
        error: () => {
          this.cancelUpload();
        },
      });
  }

  download(path: string) {
    this.session.download_in_progress = true;
    this.sessionsService.downloadFile(this.session.id, path).subscribe({
      next: (response: Blob) => {
        saveAs(
          response,
          `${path.replace(/^[/\\: ]+/, '').replace(/[/\\: ]+/g, '_')}.zip`,
        );
        this.session.download_in_progress = false;
      },
      error: () => {
        this.session.download_in_progress = false;
      },
    });
  }

  cancelUpload() {
    this.uploadProgress = null;
  }
}

type SessionWithDownloadInformation = Session & {
  download_in_progress?: boolean;
};
