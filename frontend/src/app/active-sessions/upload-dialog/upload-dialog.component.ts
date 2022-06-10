import { NestedTreeControl, FlatTreeControl } from '@angular/cdk/tree';
import { Component, OnInit, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatDialog } from '@angular/material/dialog';
import {MatTreeFlatDataSource, MatTreeFlattener} from '@angular/material/tree';

import { MatTreeNestedDataSource  } from '@angular/material/tree';
import { Subscription, finalize } from 'rxjs';
import { Session } from 'src/app/schemes';
import { LoadFilesService } from 'src/app/services/load-files/load-files.service';
import { HttpEventType } from '@angular/common/http'

import { FileExistsDialogComponent } from './file-exists-dialog/file-exists-dialog.component';

export class PathNode {
  id: number = -1;
  level: number = -1;
  name: string = "";
  children?: PathNode[];
}




@Component({
  selector: 'upload-dialog',
  templateUrl: "upload-dialog.component.html",
  styleUrls: ["upload-dialog.component.css"]
})
export class UploadDialogComponent implements OnInit{

  files:[File, string][] = [];
  private subscription: Subscription | undefined;
  uploadProgress: number | null = null;

  treeControl = new NestedTreeControl<PathNode>(node => node.children);
  dataSource = new MatTreeNestedDataSource<PathNode>();

  //treeControl: FlatTreeControl<PathNode>;

  //treeFlattener: MatTreeFlattener<PathNode>;

  //dataSource: MatTreeFlatDataSource<PathNode>;

  lastID: number = 0;

  constructor(
    private loadService: LoadFilesService,
    private dialog: MatDialog,
    public dialogRef: MatDialogRef<UploadDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public session: Session
  ) {
    /*
    this.treeFlattener = new MatTreeFlattener(
      this._transformer,
      this.getLevel,
      this.isExpandable,
      this.getChildren,
    );
    this.treeControl = new FlatTreeControl<PathNode>(this.getLevel, this.isExpandable);
    this.dataSource = new MatTreeFlatDataSource(this.treeControl, this.treeFlattener);*/

  }

  ngOnInit(): void {
    this.loadService.getCurrentFiles(this.session.id).subscribe((fileSystem: any) => {
      this.dataSource.data = [JSON.parse(fileSystem)];

      this.getLastID(this.dataSource.data[0]);
    });
  }

  hasChild = (_: number, node: PathNode) => !!node.children;

  getLevel = (node: PathNode) => node.level;

  getChildren = (node: PathNode): PathNode[] | undefined => node.children;

  isExpandable = (node: PathNode): boolean => !!node.children;

  /*transformer = (node: PathNode, level: number) => {
    const existingNode = this.nestedNodeMap.get(node);
    const flatNode =
      existingNode && existingNode.item === node.item ? existingNode : new TodoItemFlatNode();
    flatNode.item = node.item;
    flatNode.level = level;
    flatNode.expandable = !!node.children?.length;
    this.flatNodeMap.set(flatNode, node);
    this.nestedNodeMap.set(node, flatNode);
    return flatNode;
  };*/

  getLastID(node: PathNode){
    console.log(node)
    node.children?.forEach((child: PathNode) => {
      this.getLastID(child);
      if (this.lastID < child.id) this.lastID = child.id;
    })
  }

  getParentNode(node: PathNode): PathNode | null {
    const currentLevel = this.getLevel(node);

    if (currentLevel < 1) {
      return null;
    }

    var startIndex = this.treeControl.dataNodes.indexOf(node) - 1;

    for (let i = startIndex; i >= 0; i--) {
      var currentNode = this.treeControl.dataNodes[i]

      if (this.getLevel(currentNode) < currentLevel) {
        return currentNode;
      }
    }

    return null;
  }


  buildPathPrefix(node: PathNode): string {
    if (!node.level){
      return ""
    }
    return this.getParentNode(node) + `/${node.name}`
  }

  _buildFilePathPrefix(node: PathNode, names: string[], searchedID: number): string {
    if (node.id == searchedID) return "";

    var filePath = "";
    if (!!node.children){
      for (var i = 0; i < node.children.length; i++) {
        const child = node.children[i];
        if (searchedID == child.id) {
          names.forEach((name: string) => {
            filePath += `${name}/`
          })
          filePath += `${child.name}`;
          break;
        }else{
          names.push(child.name);
          filePath = this._buildFilePathPrefix(child, names, searchedID);
          const index: number = names.indexOf(child.name);
          names.splice(index, 1);
        }
      }
    }
    return filePath;
  }

  buildFilePathPrefix(id: number){
    return this._buildFilePathPrefix(this.dataSource.data[0], [], id)
  }


  onFileInput(files: FileList | null, id: number): void {
    // const prefix = this.buildPathPrefix(node);
    const prefix = this.buildFilePathPrefix(id)
    console.log(prefix);

    if (files) {
      for (let file of Array.from(files)) {
        if (this.checkIfFileExists(file, prefix)) {

          const dialogRef = this.dialog.open(
            FileExistsDialogComponent,
            {data: file.name}
          )
          dialogRef.afterClosed().subscribe(response => {
            if (! this.files.includes([file, prefix]) && response){
              this.files.push([file, prefix]);
            }
          })
        }else if (! this.files.includes([file, prefix])){
            this.files.push([file, prefix]);
        }
      }
    }
  }

  checkIfFileExists(file: File, prefix: string): boolean {
    var result = false;
    this.dataSource.data[0].children?.forEach((child: PathNode) => {
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
      console.log(file, prefix,  prefix + `/${file.name}`)
      formData.append('files', file, prefix + `/${file.name}`);
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
    window.location.reload();
  }
}