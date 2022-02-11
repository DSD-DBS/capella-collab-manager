import { Component, OnInit, Renderer2 } from '@angular/core';
import { LocalStorageService } from '../auth/local-storage/local-storage.service';
import { AuthService } from '../services/auth/auth.service';
import { RepositoryService } from '../services/repository/repository.service';
import { UserService } from '../services/user/user.service';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css'],
})
export class HeaderComponent implements OnInit {
  constructor(
    public localStorageService: LocalStorageService,
    public authService: AuthService,
    public userService: UserService,
    public repositoryService: RepositoryService
  ) {}

  ngOnInit(): void {
    let githubButtonScript = document.createElement('script');
    githubButtonScript.type = 'text/javascript';
    githubButtonScript.src = 'https://buttons.github.io/buttons.js';
    document.head.appendChild(githubButtonScript);
  }
}
