import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { environment } from 'src/environments/environment';
import { TermsConditionsComponent } from './terms-conditions/terms-conditions.component';

@Component({
  selector: 'app-footer',
  templateUrl: './footer.component.html',
  styleUrls: ['./footer.component.css'],
})
export class FooterComponent implements OnInit {
  constructor(public dialog: MatDialog) {}

  provider = environment.provider;

  ngOnInit(): void {}

  openTC(): void {
    this.dialog.open(TermsConditionsComponent);
  }
}
