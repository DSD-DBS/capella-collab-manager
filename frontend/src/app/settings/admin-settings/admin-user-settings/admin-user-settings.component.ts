import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { User } from 'src/app/schemes';
import { RepositoryUserService } from 'src/app/services/repository-user/repository-user.service';
import { UserService } from 'src/app/services/user/user.service';
import { lowerCaseValidator } from 'src/app/validators/validators';

@Component({
  selector: 'app-admin-user-settings',
  templateUrl: './admin-user-settings.component.html',
  styleUrls: ['./admin-user-settings.component.css'],
})
export class AdminUserSettingsComponent implements OnInit {
  createAdministratorFormGroup = new FormGroup({
    username: new FormControl('', [Validators.required]),
  });

  users: Array<User> = [];
  search = '';

  constructor(
    public userService: UserService,
    public repoUserService: RepositoryUserService
  ) {}

  ngOnInit(): void {
    this.getUsers();
  }

  get username(): FormControl {
    return this.createAdministratorFormGroup.get('username') as FormControl;
  }

  createAdministrator() {
    if (this.createAdministratorFormGroup.valid) {
      this.userService
        .updateRoleOfUser(
          this.createAdministratorFormGroup.value.username,
          'administrator'
        )
        .subscribe(() => {
          this.getUsers();
        });
    }
  }

  createAdministratorWithUsername(username: string) {
    this.userService
      .updateRoleOfUser(username, 'administrator')
      .subscribe(() => {
        this.getUsers();
      });
  }

  getUsers() {
    this.userService.getUsers().subscribe((res: Array<User>) => {
      this.users = res;
    });
  }

  removeAdministrator(username: string) {
    this.userService.updateRoleOfUser(username, 'user').subscribe(() => {
      this.getUsers();
    });
  }

  deleteUser(username: string) {
    this.userService.deleteUser(username).subscribe(() => {
      this.getUsers();
    });
  }

  getUsersByRole(role: 'administrator' | 'user'): Array<User> {
    return this.users.filter(
      (u) => u.role == role
      && u.name.toLowerCase().includes(this.search.toLowerCase())
    );
  }
}
