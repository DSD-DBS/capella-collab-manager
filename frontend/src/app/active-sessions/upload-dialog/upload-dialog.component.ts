import { NestedTreeControl } from '@angular/cdk/tree';
import { Component, OnInit, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatTreeNestedDataSource  } from '@angular/material/tree';
import { Subscription, finalize } from 'rxjs';
import { Session, PathNode } from 'src/app/schemes';
import { LoadFilesService } from 'src/app/services/load-files/load-files.service';
import { HttpEventType } from '@angular/common/http'


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

  lastID: number = 0;

  constructor(
    private loadService: LoadFilesService,
    public dialogRef: MatDialogRef<UploadDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public session: Session
  ) { }

  ngOnInit(): void {
    this.loadService.getCurrentFiles(this.session.id).subscribe((fileSystem: any) => {
      this.dataSource.data = [JSON.parse(fileSystem)];
      this.getLastID(this.dataSource.data[0]);
      console.log(this.dataSource.data);
    });
  }

  hasChild = (_: number, node: PathNode) => !!node.children; // && node.children.length > 0;

  hasNoContent = (_: number, _nodeData: PathNode) => _nodeData.name === '';

  getLastID(node: PathNode){
    console.log(node)
    node.children?.forEach((child: PathNode) => {
      this.getLastID(child);
      if (this.lastID < child.id) this.lastID = child.id;
    })
  }

  addNewDir(node: PathNode, name: string) {
    // TODO
    node.name = name;
    node.children = [];
    this.dataSource.data[0].children?.push(node);
  }



  pushToDatasource(node: PathNode,  newNode: PathNode, position: number){
    node.children?.forEach((child: PathNode) => {
      if (position == child.id){
        child.children?.push(newNode);
      }
    });
    console.log(this.dataSource.data);
  }

  buildFilePathPrefix(node: PathNode, names: string[], searchedID: number): any {
    if (node.id == searchedID) return "";

    node.children?.forEach((child: PathNode) => {
      if (searchedID == child.id) {
        var filePath = "";
        names.forEach((name: string) => {
          filePath += `/${name}`
        }
      )
      return filePath;
      }
      else {
        names.push(child.name);
        return this.buildFilePathPrefix(child, names, searchedID);
      }
    })
  }

  onFileInput(files: FileList | null, id: number): void {
    console.log("id" , id)
    var prefix = this.buildFilePathPrefix(this.dataSource.data[0], [], id);
    console.log("dls", prefix);
    if (files) {
      for (let file of Array.from(files)) {
        if (! this.files.includes([file, prefix])) {
          this.files.push([file, prefix]);
        }
        else {
          // TODO: Are you sure to overwrite `${file.name}`?
        }
      }
    }
  }

  removeFileFromSelection(file: File): void {
    // TODO
    const prefix = "placeholder";
    const index: number = this.files.indexOf([file, prefix]);
    this.files.splice(index, 1);
  }

  removeFileFromSystem(name: string): void {
    //TODO
  }

  placeholder() {

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