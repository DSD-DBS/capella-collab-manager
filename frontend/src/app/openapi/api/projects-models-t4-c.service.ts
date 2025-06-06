/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 *
 * Capella Collaboration Manager API
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * Do not edit the class manually.
 + To generate a new version, run `make openapi` in the root directory of this repository.
 */

/* tslint:disable:no-unused-variable member-ordering */

import { Inject, Injectable, Optional }                      from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams,
         HttpResponse, HttpEvent, HttpParameterCodec, HttpContext 
        }       from '@angular/common/http';
import { CustomHttpParameterCodec }                          from '../encoder';
import { Observable }                                        from 'rxjs';

// @ts-ignore
import { HTTPValidationError } from '../model/http-validation-error';
// @ts-ignore
import { PatchT4CModel } from '../model/patch-t4-c-model';
// @ts-ignore
import { SimpleT4CModelWithRepository } from '../model/simple-t4-c-model-with-repository';
// @ts-ignore
import { SubmitT4CModel } from '../model/submit-t4-c-model';

// @ts-ignore
import { BASE_PATH, COLLECTION_FORMATS }                     from '../variables';
import { Configuration }                                     from '../configuration';
import { BaseService } from '../api.base.service';



@Injectable({
  providedIn: 'root'
})
export class ProjectsModelsT4CService extends BaseService {

    constructor(protected httpClient: HttpClient, @Optional() @Inject(BASE_PATH) basePath: string|string[], @Optional() configuration?: Configuration) {
        super(basePath, configuration);
    }

    /**
     * Create T4C Model
     * This route requires the following permissions: &#x60;admin.t4c_repositories:update&#x60;&lt;br /&gt;&lt;br /&gt;This route requires the following permissions in the corresponding project: &#x60;t4c_model_links:create&#x60;
     * @param projectSlug 
     * @param modelSlug 
     * @param submitT4CModel 
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     */
    public createT4cModel(projectSlug: string, modelSlug: string, submitT4CModel: SubmitT4CModel, observe?: 'body', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<SimpleT4CModelWithRepository>;
    public createT4cModel(projectSlug: string, modelSlug: string, submitT4CModel: SubmitT4CModel, observe?: 'response', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<HttpResponse<SimpleT4CModelWithRepository>>;
    public createT4cModel(projectSlug: string, modelSlug: string, submitT4CModel: SubmitT4CModel, observe?: 'events', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<HttpEvent<SimpleT4CModelWithRepository>>;
    public createT4cModel(projectSlug: string, modelSlug: string, submitT4CModel: SubmitT4CModel, observe: any = 'body', reportProgress: boolean = false, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<any> {
        if (projectSlug === null || projectSlug === undefined) {
            throw new Error('Required parameter projectSlug was null or undefined when calling createT4cModel.');
        }
        if (modelSlug === null || modelSlug === undefined) {
            throw new Error('Required parameter modelSlug was null or undefined when calling createT4cModel.');
        }
        if (submitT4CModel === null || submitT4CModel === undefined) {
            throw new Error('Required parameter submitT4CModel was null or undefined when calling createT4cModel.');
        }

        let localVarHeaders = this.defaultHeaders;

        const localVarHttpHeaderAcceptSelected: string | undefined = options?.httpHeaderAccept ?? this.configuration.selectHeaderAccept([
            'application/json'
        ]);
        if (localVarHttpHeaderAcceptSelected !== undefined) {
            localVarHeaders = localVarHeaders.set('Accept', localVarHttpHeaderAcceptSelected);
        }

        const localVarHttpContext: HttpContext = options?.context ?? new HttpContext();

        const localVarTransferCache: boolean = options?.transferCache ?? true;


        // to determine the Content-Type header
        const consumes: string[] = [
            'application/json'
        ];
        const httpContentTypeSelected: string | undefined = this.configuration.selectHeaderContentType(consumes);
        if (httpContentTypeSelected !== undefined) {
            localVarHeaders = localVarHeaders.set('Content-Type', httpContentTypeSelected);
        }

        let responseType_: 'text' | 'json' | 'blob' = 'json';
        if (localVarHttpHeaderAcceptSelected) {
            if (localVarHttpHeaderAcceptSelected.startsWith('text')) {
                responseType_ = 'text';
            } else if (this.configuration.isJsonMime(localVarHttpHeaderAcceptSelected)) {
                responseType_ = 'json';
            } else {
                responseType_ = 'blob';
            }
        }

        let localVarPath = `/api/v1/projects/${this.configuration.encodeParam({name: "projectSlug", value: projectSlug, in: "path", style: "simple", explode: false, dataType: "string", dataFormat: undefined})}/models/${this.configuration.encodeParam({name: "modelSlug", value: modelSlug, in: "path", style: "simple", explode: false, dataType: "string", dataFormat: undefined})}/modelsources/t4c`;
        const { basePath, withCredentials } = this.configuration;
        return this.httpClient.request<SimpleT4CModelWithRepository>('post', `${basePath}${localVarPath}`,
            {
                context: localVarHttpContext,
                body: submitT4CModel,
                responseType: <any>responseType_,
                ...(withCredentials ? { withCredentials } : {}),
                headers: localVarHeaders,
                observe: observe,
                transferCache: localVarTransferCache,
                reportProgress: reportProgress
            }
        );
    }

    /**
     * Delete T4C Model
     * This route requires the following permissions: &#x60;admin.t4c_repositories:update&#x60;&lt;br /&gt;&lt;br /&gt;This route requires the following permissions in the corresponding project: &#x60;t4c_model_links:delete&#x60;
     * @param projectSlug 
     * @param t4cModelId 
     * @param modelSlug 
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     */
    public deleteT4cModel(projectSlug: string, t4cModelId: number, modelSlug: string, observe?: 'body', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<any>;
    public deleteT4cModel(projectSlug: string, t4cModelId: number, modelSlug: string, observe?: 'response', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<HttpResponse<any>>;
    public deleteT4cModel(projectSlug: string, t4cModelId: number, modelSlug: string, observe?: 'events', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<HttpEvent<any>>;
    public deleteT4cModel(projectSlug: string, t4cModelId: number, modelSlug: string, observe: any = 'body', reportProgress: boolean = false, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<any> {
        if (projectSlug === null || projectSlug === undefined) {
            throw new Error('Required parameter projectSlug was null or undefined when calling deleteT4cModel.');
        }
        if (t4cModelId === null || t4cModelId === undefined) {
            throw new Error('Required parameter t4cModelId was null or undefined when calling deleteT4cModel.');
        }
        if (modelSlug === null || modelSlug === undefined) {
            throw new Error('Required parameter modelSlug was null or undefined when calling deleteT4cModel.');
        }

        let localVarHeaders = this.defaultHeaders;

        const localVarHttpHeaderAcceptSelected: string | undefined = options?.httpHeaderAccept ?? this.configuration.selectHeaderAccept([
            'application/json'
        ]);
        if (localVarHttpHeaderAcceptSelected !== undefined) {
            localVarHeaders = localVarHeaders.set('Accept', localVarHttpHeaderAcceptSelected);
        }

        const localVarHttpContext: HttpContext = options?.context ?? new HttpContext();

        const localVarTransferCache: boolean = options?.transferCache ?? true;


        let responseType_: 'text' | 'json' | 'blob' = 'json';
        if (localVarHttpHeaderAcceptSelected) {
            if (localVarHttpHeaderAcceptSelected.startsWith('text')) {
                responseType_ = 'text';
            } else if (this.configuration.isJsonMime(localVarHttpHeaderAcceptSelected)) {
                responseType_ = 'json';
            } else {
                responseType_ = 'blob';
            }
        }

        let localVarPath = `/api/v1/projects/${this.configuration.encodeParam({name: "projectSlug", value: projectSlug, in: "path", style: "simple", explode: false, dataType: "string", dataFormat: undefined})}/models/${this.configuration.encodeParam({name: "modelSlug", value: modelSlug, in: "path", style: "simple", explode: false, dataType: "string", dataFormat: undefined})}/modelsources/t4c/${this.configuration.encodeParam({name: "t4cModelId", value: t4cModelId, in: "path", style: "simple", explode: false, dataType: "number", dataFormat: undefined})}`;
        const { basePath, withCredentials } = this.configuration;
        return this.httpClient.request<any>('delete', `${basePath}${localVarPath}`,
            {
                context: localVarHttpContext,
                responseType: <any>responseType_,
                ...(withCredentials ? { withCredentials } : {}),
                headers: localVarHeaders,
                observe: observe,
                transferCache: localVarTransferCache,
                reportProgress: reportProgress
            }
        );
    }

    /**
     * Get T4C Model
     * This route requires the following permissions in the corresponding project: &#x60;t4c_model_links:get&#x60;
     * @param projectSlug 
     * @param t4cModelId 
     * @param modelSlug 
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     */
    public getT4cModel(projectSlug: string, t4cModelId: number, modelSlug: string, observe?: 'body', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<SimpleT4CModelWithRepository>;
    public getT4cModel(projectSlug: string, t4cModelId: number, modelSlug: string, observe?: 'response', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<HttpResponse<SimpleT4CModelWithRepository>>;
    public getT4cModel(projectSlug: string, t4cModelId: number, modelSlug: string, observe?: 'events', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<HttpEvent<SimpleT4CModelWithRepository>>;
    public getT4cModel(projectSlug: string, t4cModelId: number, modelSlug: string, observe: any = 'body', reportProgress: boolean = false, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<any> {
        if (projectSlug === null || projectSlug === undefined) {
            throw new Error('Required parameter projectSlug was null or undefined when calling getT4cModel.');
        }
        if (t4cModelId === null || t4cModelId === undefined) {
            throw new Error('Required parameter t4cModelId was null or undefined when calling getT4cModel.');
        }
        if (modelSlug === null || modelSlug === undefined) {
            throw new Error('Required parameter modelSlug was null or undefined when calling getT4cModel.');
        }

        let localVarHeaders = this.defaultHeaders;

        const localVarHttpHeaderAcceptSelected: string | undefined = options?.httpHeaderAccept ?? this.configuration.selectHeaderAccept([
            'application/json'
        ]);
        if (localVarHttpHeaderAcceptSelected !== undefined) {
            localVarHeaders = localVarHeaders.set('Accept', localVarHttpHeaderAcceptSelected);
        }

        const localVarHttpContext: HttpContext = options?.context ?? new HttpContext();

        const localVarTransferCache: boolean = options?.transferCache ?? true;


        let responseType_: 'text' | 'json' | 'blob' = 'json';
        if (localVarHttpHeaderAcceptSelected) {
            if (localVarHttpHeaderAcceptSelected.startsWith('text')) {
                responseType_ = 'text';
            } else if (this.configuration.isJsonMime(localVarHttpHeaderAcceptSelected)) {
                responseType_ = 'json';
            } else {
                responseType_ = 'blob';
            }
        }

        let localVarPath = `/api/v1/projects/${this.configuration.encodeParam({name: "projectSlug", value: projectSlug, in: "path", style: "simple", explode: false, dataType: "string", dataFormat: undefined})}/models/${this.configuration.encodeParam({name: "modelSlug", value: modelSlug, in: "path", style: "simple", explode: false, dataType: "string", dataFormat: undefined})}/modelsources/t4c/${this.configuration.encodeParam({name: "t4cModelId", value: t4cModelId, in: "path", style: "simple", explode: false, dataType: "number", dataFormat: undefined})}`;
        const { basePath, withCredentials } = this.configuration;
        return this.httpClient.request<SimpleT4CModelWithRepository>('get', `${basePath}${localVarPath}`,
            {
                context: localVarHttpContext,
                responseType: <any>responseType_,
                ...(withCredentials ? { withCredentials } : {}),
                headers: localVarHeaders,
                observe: observe,
                transferCache: localVarTransferCache,
                reportProgress: reportProgress
            }
        );
    }

    /**
     * List T4C Models
     * This route requires the following permissions in the corresponding project: &#x60;t4c_model_links:get&#x60;
     * @param projectSlug 
     * @param modelSlug 
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     */
    public listT4cModels(projectSlug: string, modelSlug: string, observe?: 'body', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<Array<SimpleT4CModelWithRepository>>;
    public listT4cModels(projectSlug: string, modelSlug: string, observe?: 'response', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<HttpResponse<Array<SimpleT4CModelWithRepository>>>;
    public listT4cModels(projectSlug: string, modelSlug: string, observe?: 'events', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<HttpEvent<Array<SimpleT4CModelWithRepository>>>;
    public listT4cModels(projectSlug: string, modelSlug: string, observe: any = 'body', reportProgress: boolean = false, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<any> {
        if (projectSlug === null || projectSlug === undefined) {
            throw new Error('Required parameter projectSlug was null or undefined when calling listT4cModels.');
        }
        if (modelSlug === null || modelSlug === undefined) {
            throw new Error('Required parameter modelSlug was null or undefined when calling listT4cModels.');
        }

        let localVarHeaders = this.defaultHeaders;

        const localVarHttpHeaderAcceptSelected: string | undefined = options?.httpHeaderAccept ?? this.configuration.selectHeaderAccept([
            'application/json'
        ]);
        if (localVarHttpHeaderAcceptSelected !== undefined) {
            localVarHeaders = localVarHeaders.set('Accept', localVarHttpHeaderAcceptSelected);
        }

        const localVarHttpContext: HttpContext = options?.context ?? new HttpContext();

        const localVarTransferCache: boolean = options?.transferCache ?? true;


        let responseType_: 'text' | 'json' | 'blob' = 'json';
        if (localVarHttpHeaderAcceptSelected) {
            if (localVarHttpHeaderAcceptSelected.startsWith('text')) {
                responseType_ = 'text';
            } else if (this.configuration.isJsonMime(localVarHttpHeaderAcceptSelected)) {
                responseType_ = 'json';
            } else {
                responseType_ = 'blob';
            }
        }

        let localVarPath = `/api/v1/projects/${this.configuration.encodeParam({name: "projectSlug", value: projectSlug, in: "path", style: "simple", explode: false, dataType: "string", dataFormat: undefined})}/models/${this.configuration.encodeParam({name: "modelSlug", value: modelSlug, in: "path", style: "simple", explode: false, dataType: "string", dataFormat: undefined})}/modelsources/t4c`;
        const { basePath, withCredentials } = this.configuration;
        return this.httpClient.request<Array<SimpleT4CModelWithRepository>>('get', `${basePath}${localVarPath}`,
            {
                context: localVarHttpContext,
                responseType: <any>responseType_,
                ...(withCredentials ? { withCredentials } : {}),
                headers: localVarHeaders,
                observe: observe,
                transferCache: localVarTransferCache,
                reportProgress: reportProgress
            }
        );
    }

    /**
     * Update T4C Model
     * This route requires the following permissions: &#x60;admin.t4c_repositories:update&#x60;&lt;br /&gt;&lt;br /&gt;This route requires the following permissions in the corresponding project: &#x60;t4c_model_links:update&#x60;
     * @param projectSlug 
     * @param t4cModelId 
     * @param modelSlug 
     * @param patchT4CModel 
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     */
    public updateT4cModel(projectSlug: string, t4cModelId: number, modelSlug: string, patchT4CModel: PatchT4CModel, observe?: 'body', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<SimpleT4CModelWithRepository>;
    public updateT4cModel(projectSlug: string, t4cModelId: number, modelSlug: string, patchT4CModel: PatchT4CModel, observe?: 'response', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<HttpResponse<SimpleT4CModelWithRepository>>;
    public updateT4cModel(projectSlug: string, t4cModelId: number, modelSlug: string, patchT4CModel: PatchT4CModel, observe?: 'events', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<HttpEvent<SimpleT4CModelWithRepository>>;
    public updateT4cModel(projectSlug: string, t4cModelId: number, modelSlug: string, patchT4CModel: PatchT4CModel, observe: any = 'body', reportProgress: boolean = false, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<any> {
        if (projectSlug === null || projectSlug === undefined) {
            throw new Error('Required parameter projectSlug was null or undefined when calling updateT4cModel.');
        }
        if (t4cModelId === null || t4cModelId === undefined) {
            throw new Error('Required parameter t4cModelId was null or undefined when calling updateT4cModel.');
        }
        if (modelSlug === null || modelSlug === undefined) {
            throw new Error('Required parameter modelSlug was null or undefined when calling updateT4cModel.');
        }
        if (patchT4CModel === null || patchT4CModel === undefined) {
            throw new Error('Required parameter patchT4CModel was null or undefined when calling updateT4cModel.');
        }

        let localVarHeaders = this.defaultHeaders;

        const localVarHttpHeaderAcceptSelected: string | undefined = options?.httpHeaderAccept ?? this.configuration.selectHeaderAccept([
            'application/json'
        ]);
        if (localVarHttpHeaderAcceptSelected !== undefined) {
            localVarHeaders = localVarHeaders.set('Accept', localVarHttpHeaderAcceptSelected);
        }

        const localVarHttpContext: HttpContext = options?.context ?? new HttpContext();

        const localVarTransferCache: boolean = options?.transferCache ?? true;


        // to determine the Content-Type header
        const consumes: string[] = [
            'application/json'
        ];
        const httpContentTypeSelected: string | undefined = this.configuration.selectHeaderContentType(consumes);
        if (httpContentTypeSelected !== undefined) {
            localVarHeaders = localVarHeaders.set('Content-Type', httpContentTypeSelected);
        }

        let responseType_: 'text' | 'json' | 'blob' = 'json';
        if (localVarHttpHeaderAcceptSelected) {
            if (localVarHttpHeaderAcceptSelected.startsWith('text')) {
                responseType_ = 'text';
            } else if (this.configuration.isJsonMime(localVarHttpHeaderAcceptSelected)) {
                responseType_ = 'json';
            } else {
                responseType_ = 'blob';
            }
        }

        let localVarPath = `/api/v1/projects/${this.configuration.encodeParam({name: "projectSlug", value: projectSlug, in: "path", style: "simple", explode: false, dataType: "string", dataFormat: undefined})}/models/${this.configuration.encodeParam({name: "modelSlug", value: modelSlug, in: "path", style: "simple", explode: false, dataType: "string", dataFormat: undefined})}/modelsources/t4c/${this.configuration.encodeParam({name: "t4cModelId", value: t4cModelId, in: "path", style: "simple", explode: false, dataType: "number", dataFormat: undefined})}`;
        const { basePath, withCredentials } = this.configuration;
        return this.httpClient.request<SimpleT4CModelWithRepository>('patch', `${basePath}${localVarPath}`,
            {
                context: localVarHttpContext,
                body: patchT4CModel,
                responseType: <any>responseType_,
                ...(withCredentials ? { withCredentials } : {}),
                headers: localVarHeaders,
                observe: observe,
                transferCache: localVarTransferCache,
                reportProgress: reportProgress
            }
        );
    }

}
