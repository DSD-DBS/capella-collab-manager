// Copyright DB Netz AG and the capella-collab-manager contributors
// SPDX-License-Identifier: Apache-2.0

import { NestedTreeControl } from '@angular/cdk/tree';
import { Component, OnInit, Inject, OnDestroy } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatDialog } from '@angular/material/dialog';

import { Subscription, finalize, BehaviorSubject } from 'rxjs';
import { Session, PathNode } from 'src/app/schemes';
import { LoadFilesService } from 'src/app/services/load-files/load-files.service';
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

  treeControl = new NestedTreeControl<PathNode>((node) => node.children);
  dataSource = new BehaviorSubject<PathNode[]>([]);

  lastID: number = 0;

  constructor(
    private loadService: LoadFilesService,
    private dialog: MatDialog,
    public dialogRef: MatDialogRef<UploadDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public session: Session
  ) {}

  ngOnInit(): void {
    this.loadService.getCurrentFiles(this.session.id).subscribe({
      next: (file: PathNode) => {
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

  hasChild = (_: number, node: PathNode) => !!node.children;

  isExpandable = (node: PathNode): boolean => !!node.children;

  addFiles(files: FileList | null, path: string, parentNode: PathNode): void {
    if (files) {
      for (let file of Array.from(files)) {
        if (this.checkIfFileExists(parentNode, file.name)) {
          const fileExistsDialog = this.dialog.open(FileExistsDialogComponent, {
            data: file.name,
          });
          fileExistsDialog.afterClosed().subscribe((response) => {
            if (!this.files.includes([file, path]) && response) {
              this.files.push([file, path]);
              if (!!parentNode.children) {
                for (var i = 0; i < parentNode.children.length; i++) {
                  const child = parentNode.children[i];
                  if (child.name === file.name) {
                    child.isNew = true;
                    break;
                  }
                }
              }
            }
          });
        } else if (!this.files.includes([file, path])) {
          this.addFileToTree(this.dataSource.value[0], path, file.name);
          this.files.push([file, path]);

          this.treeControl.expand(this.dataSource.value[0]);
        }
      }
    }
  }

  addFileToTree(parentNode: PathNode, path: string, name: string): boolean {
    var result = false;
    if (parentNode.path === path) {
      name = name.replace(' ', '_');
      parentNode.children?.push({
        path: path + `/${name}`,
        name: name,
        type: 'file',
        children: null,
        isNew: true,
      });
      this.dataSource.next([{ ...this.dataSource.value[0] }]);
      this.treeControl.expand(parentNode);
      return true;
    } else if (!!parentNode.children) {
      for (var i = 0; i < parentNode.children.length; i++) {
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
    if (!!parentNode.children) {
      for (var i = 0; i < parentNode.children.length; i++) {
        if (fileName == parentNode.children[i].name) return true;
      }
    }
    return false;
  }

  expandToNode(node: PathNode): void {
    this._expandToNode(this.dataSource.value[0], node);
  }

  _expandToNode(parentNode: PathNode, node: PathNode): boolean {
    var result = false;
    if (node === parentNode) {
      this.treeControl.expand(parentNode);
      result = true;
    } else if (!!parentNode.children) {
      for (var i = 0; i < parentNode.children?.length; i++) {
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
    prefix: string
  ): [PathNode, number] | null {
    if (parentNode.children!!) {
      for (var i = 0; i < parentNode.children.length; i++) {
        const child = parentNode.children[i];
        if (child.name === searchedName && child.path === prefix) {
          return [parentNode, i];
        } else {
          var result = this._findNode(child, searchedName, prefix);
          if (!!result) {
            return result;
          }
        }
      }
    }
    return null;
  }

  removeFileFromTree(path: string, filename: string): void {
    const result = this.findNode(path, filename);
    if (!!result) {
      result[0].children?.splice(result[1], 1);
      this.dataSource.next([{ ...this.dataSource.value[0] }]);
      this.expandToNode(result[0]);
    }
  }

  removeFileFromSelection(path: string, filename: string): void {
    var file,
      prefix = null;
    for (var i = 0; i < this.files.length; i++) {
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

  onSubmit() {
    const formData = new FormData();
    this.files.forEach(([file, prefix]: [File, string]) => {
      formData.append('files', file, `${prefix}/${file.name}`);
    });
    formData.append('id', this.session.id);

    const upload$ = this.loadService
      .upload(this.session.id, formData)
      .pipe(finalize(() => {
        if (this.uploadProgress===100) this.dialogRef.close();
      }
      ));

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
  }
}
