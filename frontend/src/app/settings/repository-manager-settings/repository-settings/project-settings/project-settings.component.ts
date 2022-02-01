import {
  Component,
  EventEmitter,
  Input,
  OnInit,
  Output,
  ViewChild,
} from '@angular/core';
import {
  AbstractControl,
  FormControl,
  FormGroup,
  FormGroupDirective,
  ValidationErrors,
  Validators,
} from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import {
  RepositoryProject,
  RepositoryProjectService,
} from 'src/app/services/repository-project/repository-project.service';
import { ProjectDeletionDialogComponent } from './project-deletion-dialog/project-deletion-dialog.component';

@Component({
  selector: 'app-project-settings',
  templateUrl: './project-settings.component.html',
  styleUrls: ['./project-settings.component.css'],
})
export class ProjectSettingsComponent implements OnInit {
  projects: Array<RepositoryProject> = [];
  createProjectForm = new FormGroup({
    name: new FormControl('', Validators.required),
  });

  _repository: string = '';

  @ViewChild('projectsList') projectsList: any;

  @Input()
  set repository(value: string) {
    this._repository = value;
    this.refreshProjects();
  }

  get repository() {
    return this._repository;
  }

  @Output()
  projectEvent = new EventEmitter<Array<RepositoryProject>>();

  projectNonexistenceValidator(): Validators {
    return (control: AbstractControl): ValidationErrors | null => {
      for (let project of this.projects) {
        if (project.name == control.value) {
          return { projectExistsError: true };
        }
      }
      return null;
    };
  }

  constructor(
    private projectService: RepositoryProjectService,
    private dialog: MatDialog
  ) {}

  ngOnInit(): void {}

  refreshProjects(): void {
    this.projectService
      .getRepositoryProjects(this.repository)
      .subscribe((res) => {
        this.projects = res;
        this.projectEvent.emit(this.projects);
      });
  }

  createProject(formDirective: FormGroupDirective): void {
    if (this.createProjectForm.valid) {
      this.projectService
        .createRepositoryProject(
          this.repository,
          this.createProjectForm.value.name
        )
        .subscribe(() => {
          this.refreshProjects();
          formDirective.resetForm();
          this.createProjectForm.reset();
        });
    }
  }

  removeProject(project: RepositoryProject): void {
    const dialogRef = this.dialog.open(ProjectDeletionDialogComponent, {
      data: project,
    });

    dialogRef.afterClosed().subscribe((val) => {
      if (val) {
        this.refreshProjects();
      }
    });
  }

  get selectedProject(): RepositoryProject {
    return this.projectsList.selectedOptions.selected[0].value;
  }
}
