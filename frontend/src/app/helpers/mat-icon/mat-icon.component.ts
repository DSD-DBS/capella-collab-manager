import { Component, Input, OnInit } from '@angular/core';

@Component({
  selector: 'app-mat-icon',
  templateUrl: './mat-icon.component.html',
  styleUrls: ['./mat-icon.component.css'],
})
export class MatIconComponent implements OnInit {
  @Input() position: MatIconPosition = null;
  @Input() size: string = '24px';

  @Input() usage: MatIconUsage = 'general';
  style = {};

  constructor() {}

  ngOnInit(): void {
    this.style = {
      width: this.size,
      height: this.size,
      'font-size': this.size,
      position: 'relative',
      top: this.mapUsageToCSSRelativeTop(this.usage),
      'margin-right': '0px',
    };
  }

  mapUsageToCSSRelativeTop(usage: MatIconUsage): string {
    switch (usage) {
      case 'button': {
        return '7px';
      }
      case 'text': {
        return '4px';
      }
      default: {
        return '0px';
      }
    }
  }
}

type MatIconPosition = 'right' | 'left' | null;
type MatIconUsage = 'button' | 'text' | 'general';
