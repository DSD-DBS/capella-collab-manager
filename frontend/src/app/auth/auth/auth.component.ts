import {
  Component,
  Input,
  OnChanges,
  OnInit,
  SimpleChanges,
} from '@angular/core';
import { AuthService } from 'src/app/services/auth/auth.service';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-auth',
  templateUrl: './auth.component.html',
  styleUrls: ['./auth.component.css'],
})
export class AuthComponent implements OnInit {
  @Input()
  set autoLogin(value: boolean) {
    if (value) {
      this.webSSO();
    }
  }

  authProvider = environment.authentication;

  constructor(private authService: AuthService) {}

  ngOnInit(): void {}

  webSSO() {
    this.authService.getRedirectURL().subscribe((res) => {
      window.location.href = res.auth_url;
    });
  }
}
