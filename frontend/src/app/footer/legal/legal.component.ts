import { Component, OnInit } from '@angular/core';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-legal',
  templateUrl: './legal.component.html',
  styleUrls: ['./legal.component.css'],
})
export class LegalComponent implements OnInit {
  imprint = environment.imprint;
  privacy = environment.privacy;

  constructor() {}

  ngOnInit(): void {}
}
