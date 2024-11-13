/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 */
import { ActivatedRoute, convertToParamMap, Params } from '@angular/router';
import { BehaviorSubject } from 'rxjs';

class MockActivatedRoute {
  _queryParams = new BehaviorSubject<Params>({});
  queryParams = this._queryParams.asObservable();
  params = this._queryParams.asObservable();

  _queryParamMap = new BehaviorSubject(convertToParamMap({}));
  queryParamMap = this._queryParamMap.asObservable();

  constructor(params: Params) {
    this._queryParams.next(params);
    this._queryParamMap.next(convertToParamMap(params));
  }
}

export const mockActivatedRouteProvider = (params: Params) => {
  return {
    provide: ActivatedRoute,
    useValue: new MockActivatedRoute(params),
  };
};
