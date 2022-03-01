import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class BeautifyService {
  constructor() {}

  beatifyState(state: string | undefined): SessionState {
    let text = state;
    let css = 'warning';
    switch (state) {
      case '404':
        text = 'Error: Session not found';
        css = 'error';
        break;
      case 'pending':
        text = 'Waiting for resources';
        css = 'warning';
        break;
      case 'ImagePullBackOff':
      case 'ErrImagePull':
        text = 'Failed to pull image';
        css = 'error';
        break;
      case 'ContainerCreating':
        text = 'Creating session';
        css = 'warning';
        break;
      case 'Running':
        text = 'Running';
        css = 'success';
        break;
      case 'START_LOAD_MODEL':
        text = 'Modelloading started';
        css = 'warning';
        break;
      case 'FINISH_LOAD_MODEL':
        text = 'Modelloading finished';
        css = 'warning';
        break;
      case 'FAILURE_LOAD_MODEL':
        text = 'Error during loading of the model';
        css = 'error';
        break;
      case 'START_PREPARE_WORKSPACE':
        text = 'Started workspace preparation';
        css = 'warning';
        break;
      case 'FINISH_PREPARE_WORKSPACE':
        text = 'Workspace preparation finished';
        css = 'warning';
        break;
      case 'FAILURE_PREPARE_WORKSPACE':
        text = 'Error during workspace preparation';
        css = 'error';
        break;
      case 'START_SESSION':
        text = 'Session started';
        css = 'success';
        break;
      case 'unknown':
        text = 'Unknown State';
        css = 'primary';
        break;
      case 'Unschedulable':
        text = 'Unschedulable';
        css = 'error';
        break;
      case 'NOT_FOUND':
        text = 'Not found';
        css = 'error';
        break;
    }

    return {
      text: text || '',
      css: css,
    };
  }

  beatifyDate(date: string): string {
    const newDate = new Date(date);
    const now = new Date();
    let newDateString = '';
    if (
      newDate.getFullYear() == now.getFullYear() &&
      newDate.getMonth() == now.getMonth() &&
      newDate.getDate() == now.getDate()
    ) {
      newDateString = 'today';
    } else {
      newDateString =
        'on ' +
        newDate.toLocaleDateString(undefined, {
          year: 'numeric',
          month: 'numeric',
          day: 'numeric',
        });
    }

    return (
      newDateString +
      ' at ' +
      newDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    );
  }
}

export interface SessionState {
  text: string;
  css: string;
}
