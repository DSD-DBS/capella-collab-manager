import {
  Component,
  Input,
  OnInit,
  SimpleChanges,
  ViewChild,
} from '@angular/core';
import {
  AbstractControl,
  FormControl,
  FormGroup,
  ValidationErrors,
  ValidatorFn,
  Validators,
} from '@angular/forms';
import { RepositoryUser } from 'src/app/schemes';
import { RepositoryUserService } from 'src/app/services/repository-user/repository-user.service';
import { UserService } from 'src/app/services/user/user.service';
import { lowerCaseValidator } from 'src/app/validators/validators';

@Component({
  selector: 'app-repository-user-settings',
  templateUrl: './repository-user-settings.component.html',
  styleUrls: ['./repository-user-settings.component.css'],
})
export class RepositoryUserSettingsComponent implements OnInit {
  _repository: string = '';

  @Input()
  set repository(value: string) {
    this._repository = value;
    this.refreshRepoUsers();
  }

  get repository() {
    return this._repository;
  }

  repositoryUsers: Array<RepositoryUser> = [];
  search = '';

  @ViewChild('users') users: any;

  addUserToRepoForm = new FormGroup(
    {
      username: new FormControl('', [
        Validators.required,
        lowerCaseValidator(),
        this.userAlreadyInRepositoryValidator(),
      ]),
      role: new FormControl('', Validators.required),
      permission: new FormControl(''),
    },
    this.permissionRequiredValidator()
  );
  constructor(
    public repoUserService: RepositoryUserService,
    public userService: UserService
  ) {}

  ngOnInit(): void {}

  get username(): FormControl {
    return this.addUserToRepoForm.get('username') as FormControl;
  }

  get selectedUser(): RepositoryUser {
    return this.users.selectedOptions.selected[0].value;
  }

  permissionRequiredValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      if (
        control.get('permission')?.value in this.repoUserService.PERMISSIONS ||
        control.get('role')?.value == 'manager'
      ) {
        control.get('permission')?.setErrors(null);
        return null;
      }
      control.get('permission')?.setErrors({ permissionInvalid: true });
      return {};
    };
  }

  userAlreadyInRepositoryValidator(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      for (let repoUser of this.repositoryUsers) {
        if (repoUser.username == control.value) {
          return { userAlreadyInRepositoryError: true };
        }
      }
      return null;
    };
  }

  refreshRepoUsers(): void {
    this.repoUserService.getRepoUsers(this.repository).subscribe((res) => {
      this.repositoryUsers = res;
    });
  }

  addUser(): void {
    if (this.addUserToRepoForm.valid) {
      const formValue = this.addUserToRepoForm.value;

      let permission = formValue.permission;
      if (formValue.role == 'manager') {
        permission = 'write';
      }
      this.repoUserService
        .addUserToRepo(
          this.repository,
          formValue.username,
          formValue.role,
          permission
        )
        .subscribe(() => {
          this.refreshRepoUsers();
        });
    }
  }

  removeUserFromRepo(username: string): void {
    this.repoUserService
      .deleteUserFromRepo(this.repository, username)
      .subscribe(() => {
        this.refreshRepoUsers();
      });
  }

  upgradeUserToRepositoryManager(username: string): void {
    this.repoUserService
      .changeRoleOfRepoUser(this.repository, username, 'manager')
      .subscribe(() => {
        this.refreshRepoUsers();
      });
  }

  downgradeUserToUserRole(username: string): void {
    this.repoUserService
      .changeRoleOfRepoUser(this.repository, username, 'user')
      .subscribe(() => {
        this.refreshRepoUsers();
      });
  }

  setUserPermission(username: string, permission: 'read' | 'write'): void {
    this.repoUserService
      .changePermissionOfRepoUser(this.repository, username, permission)
      .subscribe(() => {
        this.refreshRepoUsers();
      });
  }

  getRepositoryUsersByRole(role: 'manager' | 'user'): Array<RepositoryUser> {
    return this.repositoryUsers.filter(
      (u) => u.role == role && u.username.includes(this.search.toLowerCase())
    );
  }
}
