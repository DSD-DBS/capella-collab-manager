/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { SafeResourceUrl } from '@angular/platform-browser';
import { Meta, moduleMetadata, StoryObj } from '@storybook/angular';
import { BehaviorSubject } from 'rxjs';
import { SessionPreparationState, SessionState } from 'src/app/openapi';
import {
  SessionViewerService,
  ViewerSession,
} from 'src/app/sessions/session/session-viewer.service';
import {
  mockPersistentSession,
  mockReadonlySession,
} from 'src/storybook/session';
import { SessionViewerComponent } from './session-viewer.component';

const meta: Meta<SessionViewerComponent> = {
  title: 'Session Components/Session Viewer',
  component: SessionViewerComponent,
};

export default meta;
type Story = StoryObj<SessionViewerComponent>;

class MockSessionViewerService implements Partial<SessionViewerService> {
  private _sessions = new BehaviorSubject<ViewerSession[] | undefined>(
    undefined,
  );
  public readonly sessions$ = this._sessions.asObservable();
  public readonly allSessions$ = this._sessions.asObservable();

  constructor(sessions: ViewerSession[] | undefined) {
    this._sessions.next(sessions);
  }

  // eslint-disable-next-line @typescript-eslint/no-empty-function
  clearSessions(): void {}
}

const mockPersistentViewerSession: ViewerSession = {
  ...mockPersistentSession,
  safeResourceURL: 'about:blank' as SafeResourceUrl,
  focused: true,
  reloadToResize: false,
  fullscreen: false,
  disabled: false,
  connectionInfo: {
    local_storage: {},
    t4c_token: 'token',
    redirect_url: 'about:blank',
  },
};

const mockReadOnlyViewerSession: ViewerSession = {
  ...mockReadonlySession,
  safeResourceURL: 'about:blank' as SafeResourceUrl,
  focused: false,
  reloadToResize: false,
  fullscreen: false,
  disabled: false,
};

const mockSessionServiceProvider = (sessions: ViewerSession[] | undefined) => {
  return {
    provide: SessionViewerService,
    useValue: new MockSessionViewerService(sessions),
  };
};

export const Loading: Story = {};

export const OneSuccessfulSession: Story = {
  decorators: [
    moduleMetadata({
      providers: [mockSessionServiceProvider([mockPersistentViewerSession])],
    }),
  ],
};

export const TwoSessionsTiling: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockSessionServiceProvider([
          mockPersistentViewerSession,
          mockReadOnlyViewerSession,
        ]),
      ],
    }),
  ],
};

export const TwoSessionsTilingPending: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockSessionServiceProvider([
          {
            ...mockPersistentViewerSession,
            preparation_state: SessionPreparationState.Pending,
            state: SessionState.Pending,
          },
          {
            ...mockReadOnlyViewerSession,
            preparation_state: SessionPreparationState.Completed,
            state: SessionState.Failed,
          },
        ]),
      ],
    }),
  ],
};

export const OneSessionTilingPending: Story = {
  args: {},
  decorators: [
    moduleMetadata({
      providers: [
        mockSessionServiceProvider([
          {
            ...mockPersistentViewerSession,
            preparation_state: SessionPreparationState.Completed,
            state: SessionState.Pending,
          },
        ]),
      ],
    }),
  ],
};
