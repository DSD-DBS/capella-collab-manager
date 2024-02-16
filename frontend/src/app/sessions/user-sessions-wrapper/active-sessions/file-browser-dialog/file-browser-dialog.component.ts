/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */

import { NestedTreeControl } from '@angular/cdk/tree';
import { HttpEvent, HttpEventType } from '@angular/common/http';
import { Component, Inject, OnInit } from '@angular/core';
import { FormControl } from '@angular/forms';
import {
  MAT_DIALOG_DATA,
  MatDialog,
  MatDialogRef,
} from '@angular/material/dialog';
import { saveAs } from 'file-saver';
import { BehaviorSubject } from 'rxjs';
import { ToastService } from 'src/app/helpers/toast/toast.service';
import {
  LoadFilesService,
  UploadResponse,
} from 'src/app/services/load-files/load-files.service';
import { PathNode, Session } from 'src/app/sessions/service/session.service';
import { FileExistsDialogComponent } from './file-exists-dialog/file-exists-dialog.component';

@Component({
  selector: 'app-file-browser-dialog',
  templateUrl: 'file-browser-dialog.component.html',
  styleUrls: ['file-browser-dialog.component.css'],
})
export class FileBrowserDialogComponent implements OnInit {
  files: Array<[File, string]> = [];
  uploadProgress: number | null = null;
  loadingFiles = false;

  treeControl = new NestedTreeControl<PathNode>((node) => node.children);
  dataSource = new BehaviorSubject<PathNode[]>([]);

  constructor(
    private loadService: LoadFilesService,
    private dialog: MatDialog,
    public dialogRef: MatDialogRef<FileBrowserDialogComponent>,
    private toastService: ToastService,
    @Inject(MAT_DIALOG_DATA) public session: Session,
  ) {}

  showHiddenFiles = new FormControl(false);

  ngOnInit(): void {
    this.loadFiles();
  }

  loadFiles(): void {
    this.loadingFiles = true;

    this.loadService
      .getCurrentFiles(this.session.id, this.showHiddenFiles.value as boolean)
      .subscribe({
        next: (file: PathNode) => {
          this.dataSource.next([file]);
        },
        complete: () => {
          this.loadingFiles = false;
        },
      });
  }

  hasChild = (_: number, node: PathNode) => !!node.children;

  addFiles(files: FileList | null, path: string, parentNode: PathNode): void {
    if (files) {
      for (const file of Array.from(files)) {
        const name = file.name.replace(/\s/g, '_');
        if (this.checkIfFileExists(parentNode, name)) {
          const fileExistsDialog = this.dialog.open(FileExistsDialogComponent, {
            data: name,
          });
          fileExistsDialog.afterClosed().subscribe((response) => {
            if (!this.files.includes([file, path]) && response) {
              this.files.push([file, path]);
              if (parentNode.children) {
                for (let i = 0; i < parentNode.children.length; i++) {
                  const child = parentNode.children[i];
                  if (child.name === name) {
                    child.isNew = true;
                    break;
                  }
                }
              }
            }
          });
        } else if (!this.files.includes([file, path])) {
          this.addFileToTree(this.dataSource.value[0], path, name);
          this.files.push([file, path]);
          this.treeControl.expand(this.dataSource.value[0]);
        }
      }
    }
  }

  addFileToTree(parentNode: PathNode, path: string, name: string): boolean {
    let result = false;
    if (parentNode.path === path) {
      parentNode.children?.push({
        path: path + `/${name}`,
        name,
        type: 'file',
        children: null,
        isNew: true,
      });
      this.dataSource.next([{ ...this.dataSource.value[0] }]);
      this.treeControl.expand(parentNode);
      return true;
    } else if (parentNode.children) {
      for (let i = 0; i < parentNode.children.length; i++) {
        const child = parentNode.children[i];
        result = this.addFileToTree(child, path, name);
        if (result) {
          this.treeControl.expand(parentNode);
          break;
        }
      }
    }
    return result;
  }

  checkIfFileExists(parentNode: PathNode, fileName: string): boolean {
    if (parentNode.children) {
      for (let i = 0; i < parentNode.children.length; i++) {
        if (fileName == parentNode.children[i].name) return true;
      }
    }
    return false;
  }

  expandToNode(node: PathNode): void {
    this._expandToNode(this.dataSource.value[0], node);
  }

  _expandToNode(parentNode: PathNode, node: PathNode): boolean {
    let result = false;
    if (node.path === parentNode.path) {
      this.treeControl.expand(parentNode);
      result = true;
    } else if (parentNode.children) {
      for (let i = 0; i < parentNode.children?.length; i++) {
        result = this._expandToNode(parentNode.children[i], node);
        if (result) {
          this.treeControl.expand(parentNode);
        }
      }
    }
    return result;
  }

  removeFile(path: string, filename: string): void {
    this.removeFileFromSelection(path, filename);
    this.removeFileFromTree(path, filename);
  }

  findNode(prefix: string, searchedName: string): [PathNode, number] | null {
    return this._findNode(this.dataSource.value[0], searchedName, prefix);
  }

  _findNode(
    parentNode: PathNode,
    searchedName: string,
    prefix: string,
  ): [PathNode, number] | null {
    if (parentNode.children!) {
      for (let i = 0; i < parentNode.children.length; i++) {
        const child = parentNode.children[i];
        if (child.name === searchedName && child.path === prefix) {
          return [parentNode, i];
        } else {
          const result = this._findNode(child, searchedName, prefix);
          if (result) {
            return result;
          }
        }
      }
    }
    return null;
  }

  removeFileFromTree(path: string, filename: string): void {
    const result = this.findNode(path, filename);
    if (result) {
      result[0].children?.splice(result[1], 1);
      this.dataSource.next([{ ...this.dataSource.value[0] }]);
      this.expandToNode(result[0]);
    }
  }

  removeFileFromSelection(path: string, filename: string): void {
    let file;
    let prefix = null;
    for (let i = 0; i < this.files.length; i++) {
      file = this.files[i][0];
      prefix = this.files[i][1];
      if (this.files[i][0].name === filename && this.files[i][1] === path) {
        break;
      }
    }
    if (!!file && !!prefix) {
      const index: number = this.files.indexOf([file, prefix]);
      this.files.splice(index, 1);
    }
  }

  submit() {
    const formData = new FormData();
    let size = 0;
    this.files.forEach(([file, _]: [File, string]) => {
      size += file.size;
    });

    if (size > 31457280) {
      this.toastService.showError(
        'File too large!',
        'The file size must not exceed 30MB!',
      );
      return;
    }

    this.files.forEach(([file, prefix]: [File, string]) => {
      formData.append('files', file, `${prefix}/${file.name}`);
    });
    formData.append('id', this.session.id);

    this.loadService.upload(this.session.id, formData).subscribe({
      next: (event: HttpEvent<UploadResponse>) => {
        if (event.type == HttpEventType.Response) {
          this.dialogRef.close();
        } else if (event.type == HttpEventType.UploadProgress && event.total) {
          this.uploadProgress = Math.round(100 * (event.loaded / event.total));
        }
      },
      error: () => {
        this.reset();
      },
    });
  }

  download(filename: string) {
    this.session.download_in_progress = true;
    this.loadService.download(this.session.id, filename).subscribe({
      next: (response: Blob) => {
        saveAs(
          response,
          `${filename
            .replace(/^[\/\\: ]+/, '')
            .replace(/[\/\\: ]+/g, '_')}.zip`,
        );
        this.session.download_in_progress = false;
      },
      error: () => {
        this.session.download_in_progress = false;
      },
    });
  }

  reset() {
    this.uploadProgress = null;
  }
}
