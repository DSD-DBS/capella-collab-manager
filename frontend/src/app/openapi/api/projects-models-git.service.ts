/*
 * SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 * SPDX-License-Identifier: Apache-2.0
 *
 * Capella Collaboration
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
import { GetRevisionsResponseModel } from '../model/get-revisions-response-model';
// @ts-ignore
import { GitModel } from '../model/git-model';
// @ts-ignore
import { HTTPValidationError } from '../model/http-validation-error';
// @ts-ignore
import { PatchGitModel } from '../model/patch-git-model';
// @ts-ignore
import { PostGitModel } from '../model/post-git-model';

// @ts-ignore
import { BASE_PATH, COLLECTION_FORMATS }                     from '../variables';
import { Configuration }                                     from '../configuration';



@Injectable({
  providedIn: 'root'
})
export class ProjectsModelsGitService {

    protected basePath = 'http://localhost';
    public defaultHeaders = new HttpHeaders();
    public configuration = new Configuration();
    public encoder: HttpParameterCodec;

    constructor(protected httpClient: HttpClient, @Optional()@Inject(BASE_PATH) basePath: string|string[], @Optional() configuration: Configuration) {
        if (configuration) {
            this.configuration = configuration;
        }
        if (typeof this.configuration.basePath !== 'string') {
            const firstBasePath = Array.isArray(basePath) ? basePath[0] : undefined;
            if (firstBasePath != undefined) {
                basePath = firstBasePath;
            }

            if (typeof basePath !== 'string') {
                basePath = this.basePath;
            }
            this.configuration.basePath = basePath;
        }
        this.encoder = this.configuration.encoder || new CustomHttpParameterCodec();
    }


    // @ts-ignore
    private addToHttpParams(httpParams: HttpParams, value: any, key?: string): HttpParams {
        if (typeof value === "object" && value instanceof Date === false) {
            httpParams = this.addToHttpParamsRecursive(httpParams, value);
        } else {
            httpParams = this.addToHttpParamsRecursive(httpParams, value, key);
        }
        return httpParams;
    }

    private addToHttpParamsRecursive(httpParams: HttpParams, value?: any, key?: string): HttpParams {
        if (value == null) {
            return httpParams;
        }

        if (typeof value === "object") {
            if (Array.isArray(value)) {
                (value as any[]).forEach( elem => httpParams = this.addToHttpParamsRecursive(httpParams, elem, key));
            } else if (value instanceof Date) {
                if (key != null) {
                    httpParams = httpParams.append(key, (value as Date).toISOString().substring(0, 10));
                } else {
                   throw Error("key may not be null if value is Date");
                }
            } else {
                Object.keys(value).forEach( k => httpParams = this.addToHttpParamsRecursive(
                    httpParams, value[k], key != null ? `${key}.${k}` : k));
            }
        } else if (key != null) {
            httpParams = httpParams.append(key, value);
        } else {
            throw Error("key may not be null if value is not object or array");
        }
        return httpParams;
    }

    /**
     * Create Git Model
     * @param projectSlug 
     * @param modelSlug 
     * @param postGitModel 
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     */
    public createGitModel(projectSlug: string, modelSlug: string, postGitModel: PostGitModel, observe?: 'body', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<GitModel>;
    public createGitModel(projectSlug: string, modelSlug: string, postGitModel: PostGitModel, observe?: 'response', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<HttpResponse<GitModel>>;
    public createGitModel(projectSlug: string, modelSlug: string, postGitModel: PostGitModel, observe?: 'events', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<HttpEvent<GitModel>>;
    public createGitModel(projectSlug: string, modelSlug: string, postGitModel: PostGitModel, observe: any = 'body', reportProgress: boolean = false, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<any> {
        if (projectSlug === null || projectSlug === undefined) {
            throw new Error('Required parameter projectSlug was null or undefined when calling createGitModel.');
        }
        if (modelSlug === null || modelSlug === undefined) {
            throw new Error('Required parameter modelSlug was null or undefined when calling createGitModel.');
        }
        if (postGitModel === null || postGitModel === undefined) {
            throw new Error('Required parameter postGitModel was null or undefined when calling createGitModel.');
        }

        let localVarHeaders = this.defaultHeaders;

        let localVarCredential: string | undefined;
        // authentication (PersonalAccessToken) required
        localVarCredential = this.configuration.lookupCredential('PersonalAccessToken');
        if (localVarCredential) {
            localVarHeaders = localVarHeaders.set('Authorization', 'Basic ' + localVarCredential);
        }

        let localVarHttpHeaderAcceptSelected: string | undefined = options && options.httpHeaderAccept;
        if (localVarHttpHeaderAcceptSelected === undefined) {
            // to determine the Accept header
            const httpHeaderAccepts: string[] = [
                'application/json'
            ];
            localVarHttpHeaderAcceptSelected = this.configuration.selectHeaderAccept(httpHeaderAccepts);
        }
        if (localVarHttpHeaderAcceptSelected !== undefined) {
            localVarHeaders = localVarHeaders.set('Accept', localVarHttpHeaderAcceptSelected);
        }

        let localVarHttpContext: HttpContext | undefined = options && options.context;
        if (localVarHttpContext === undefined) {
            localVarHttpContext = new HttpContext();
        }

        let localVarTransferCache: boolean | undefined = options && options.transferCache;
        if (localVarTransferCache === undefined) {
            localVarTransferCache = true;
        }


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

        let localVarPath = `/api/v1/projects/${this.configuration.encodeParam({name: "projectSlug", value: projectSlug, in: "path", style: "simple", explode: false, dataType: "string", dataFormat: undefined})}/models/${this.configuration.encodeParam({name: "modelSlug", value: modelSlug, in: "path", style: "simple", explode: false, dataType: "string", dataFormat: undefined})}/modelsources/git`;
        return this.httpClient.request<GitModel>('post', `${this.configuration.basePath}${localVarPath}`,
            {
                context: localVarHttpContext,
                body: postGitModel,
                responseType: <any>responseType_,
                withCredentials: this.configuration.withCredentials,
                headers: localVarHeaders,
                observe: observe,
                transferCache: localVarTransferCache,
                reportProgress: reportProgress
            }
        );
    }

    /**
     * Delete Git Model By Id
     * @param projectSlug 
     * @param gitModelId 
     * @param modelSlug 
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     */
    public deleteGitModelById(projectSlug: string, gitModelId: number, modelSlug: string, observe?: 'body', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<any>;
    public deleteGitModelById(projectSlug: string, gitModelId: number, modelSlug: string, observe?: 'response', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<HttpResponse<any>>;
    public deleteGitModelById(projectSlug: string, gitModelId: number, modelSlug: string, observe?: 'events', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<HttpEvent<any>>;
    public deleteGitModelById(projectSlug: string, gitModelId: number, modelSlug: string, observe: any = 'body', reportProgress: boolean = false, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<any> {
        if (projectSlug === null || projectSlug === undefined) {
            throw new Error('Required parameter projectSlug was null or undefined when calling deleteGitModelById.');
        }
        if (gitModelId === null || gitModelId === undefined) {
            throw new Error('Required parameter gitModelId was null or undefined when calling deleteGitModelById.');
        }
        if (modelSlug === null || modelSlug === undefined) {
            throw new Error('Required parameter modelSlug was null or undefined when calling deleteGitModelById.');
        }

        let localVarHeaders = this.defaultHeaders;

        let localVarCredential: string | undefined;
        // authentication (PersonalAccessToken) required
        localVarCredential = this.configuration.lookupCredential('PersonalAccessToken');
        if (localVarCredential) {
            localVarHeaders = localVarHeaders.set('Authorization', 'Basic ' + localVarCredential);
        }

        let localVarHttpHeaderAcceptSelected: string | undefined = options && options.httpHeaderAccept;
        if (localVarHttpHeaderAcceptSelected === undefined) {
            // to determine the Accept header
            const httpHeaderAccepts: string[] = [
                'application/json'
            ];
            localVarHttpHeaderAcceptSelected = this.configuration.selectHeaderAccept(httpHeaderAccepts);
        }
        if (localVarHttpHeaderAcceptSelected !== undefined) {
            localVarHeaders = localVarHeaders.set('Accept', localVarHttpHeaderAcceptSelected);
        }

        let localVarHttpContext: HttpContext | undefined = options && options.context;
        if (localVarHttpContext === undefined) {
            localVarHttpContext = new HttpContext();
        }

        let localVarTransferCache: boolean | undefined = options && options.transferCache;
        if (localVarTransferCache === undefined) {
            localVarTransferCache = true;
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

        let localVarPath = `/api/v1/projects/${this.configuration.encodeParam({name: "projectSlug", value: projectSlug, in: "path", style: "simple", explode: false, dataType: "string", dataFormat: undefined})}/models/${this.configuration.encodeParam({name: "modelSlug", value: modelSlug, in: "path", style: "simple", explode: false, dataType: "string", dataFormat: undefined})}/modelsources/git/${this.configuration.encodeParam({name: "gitModelId", value: gitModelId, in: "path", style: "simple", explode: false, dataType: "number", dataFormat: undefined})}`;
        return this.httpClient.request<any>('delete', `${this.configuration.basePath}${localVarPath}`,
            {
                context: localVarHttpContext,
                responseType: <any>responseType_,
                withCredentials: this.configuration.withCredentials,
                headers: localVarHeaders,
                observe: observe,
                transferCache: localVarTransferCache,
                reportProgress: reportProgress
            }
        );
    }

    /**
     * Get Git Model By Id
     * @param projectSlug 
     * @param gitModelId 
     * @param modelSlug 
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     */
    public getGitModelById(projectSlug: string, gitModelId: number, modelSlug: string, observe?: 'body', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<GitModel>;
    public getGitModelById(projectSlug: string, gitModelId: number, modelSlug: string, observe?: 'response', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<HttpResponse<GitModel>>;
    public getGitModelById(projectSlug: string, gitModelId: number, modelSlug: string, observe?: 'events', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<HttpEvent<GitModel>>;
    public getGitModelById(projectSlug: string, gitModelId: number, modelSlug: string, observe: any = 'body', reportProgress: boolean = false, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<any> {
        if (projectSlug === null || projectSlug === undefined) {
            throw new Error('Required parameter projectSlug was null or undefined when calling getGitModelById.');
        }
        if (gitModelId === null || gitModelId === undefined) {
            throw new Error('Required parameter gitModelId was null or undefined when calling getGitModelById.');
        }
        if (modelSlug === null || modelSlug === undefined) {
            throw new Error('Required parameter modelSlug was null or undefined when calling getGitModelById.');
        }

        let localVarHeaders = this.defaultHeaders;

        let localVarCredential: string | undefined;
        // authentication (PersonalAccessToken) required
        localVarCredential = this.configuration.lookupCredential('PersonalAccessToken');
        if (localVarCredential) {
            localVarHeaders = localVarHeaders.set('Authorization', 'Basic ' + localVarCredential);
        }

        let localVarHttpHeaderAcceptSelected: string | undefined = options && options.httpHeaderAccept;
        if (localVarHttpHeaderAcceptSelected === undefined) {
            // to determine the Accept header
            const httpHeaderAccepts: string[] = [
                'application/json'
            ];
            localVarHttpHeaderAcceptSelected = this.configuration.selectHeaderAccept(httpHeaderAccepts);
        }
        if (localVarHttpHeaderAcceptSelected !== undefined) {
            localVarHeaders = localVarHeaders.set('Accept', localVarHttpHeaderAcceptSelected);
        }

        let localVarHttpContext: HttpContext | undefined = options && options.context;
        if (localVarHttpContext === undefined) {
            localVarHttpContext = new HttpContext();
        }

        let localVarTransferCache: boolean | undefined = options && options.transferCache;
        if (localVarTransferCache === undefined) {
            localVarTransferCache = true;
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

        let localVarPath = `/api/v1/projects/${this.configuration.encodeParam({name: "projectSlug", value: projectSlug, in: "path", style: "simple", explode: false, dataType: "string", dataFormat: undefined})}/models/${this.configuration.encodeParam({name: "modelSlug", value: modelSlug, in: "path", style: "simple", explode: false, dataType: "string", dataFormat: undefined})}/modelsources/git/${this.configuration.encodeParam({name: "gitModelId", value: gitModelId, in: "path", style: "simple", explode: false, dataType: "number", dataFormat: undefined})}`;
        return this.httpClient.request<GitModel>('get', `${this.configuration.basePath}${localVarPath}`,
            {
                context: localVarHttpContext,
                responseType: <any>responseType_,
                withCredentials: this.configuration.withCredentials,
                headers: localVarHeaders,
                observe: observe,
                transferCache: localVarTransferCache,
                reportProgress: reportProgress
            }
        );
    }

    /**
     * Get Git Models
     * @param projectSlug 
     * @param modelSlug 
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     */
    public getGitModels(projectSlug: string, modelSlug: string, observe?: 'body', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<Array<GitModel>>;
    public getGitModels(projectSlug: string, modelSlug: string, observe?: 'response', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<HttpResponse<Array<GitModel>>>;
    public getGitModels(projectSlug: string, modelSlug: string, observe?: 'events', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<HttpEvent<Array<GitModel>>>;
    public getGitModels(projectSlug: string, modelSlug: string, observe: any = 'body', reportProgress: boolean = false, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<any> {
        if (projectSlug === null || projectSlug === undefined) {
            throw new Error('Required parameter projectSlug was null or undefined when calling getGitModels.');
        }
        if (modelSlug === null || modelSlug === undefined) {
            throw new Error('Required parameter modelSlug was null or undefined when calling getGitModels.');
        }

        let localVarHeaders = this.defaultHeaders;

        let localVarCredential: string | undefined;
        // authentication (PersonalAccessToken) required
        localVarCredential = this.configuration.lookupCredential('PersonalAccessToken');
        if (localVarCredential) {
            localVarHeaders = localVarHeaders.set('Authorization', 'Basic ' + localVarCredential);
        }

        let localVarHttpHeaderAcceptSelected: string | undefined = options && options.httpHeaderAccept;
        if (localVarHttpHeaderAcceptSelected === undefined) {
            // to determine the Accept header
            const httpHeaderAccepts: string[] = [
                'application/json'
            ];
            localVarHttpHeaderAcceptSelected = this.configuration.selectHeaderAccept(httpHeaderAccepts);
        }
        if (localVarHttpHeaderAcceptSelected !== undefined) {
            localVarHeaders = localVarHeaders.set('Accept', localVarHttpHeaderAcceptSelected);
        }

        let localVarHttpContext: HttpContext | undefined = options && options.context;
        if (localVarHttpContext === undefined) {
            localVarHttpContext = new HttpContext();
        }

        let localVarTransferCache: boolean | undefined = options && options.transferCache;
        if (localVarTransferCache === undefined) {
            localVarTransferCache = true;
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

        let localVarPath = `/api/v1/projects/${this.configuration.encodeParam({name: "projectSlug", value: projectSlug, in: "path", style: "simple", explode: false, dataType: "string", dataFormat: undefined})}/models/${this.configuration.encodeParam({name: "modelSlug", value: modelSlug, in: "path", style: "simple", explode: false, dataType: "string", dataFormat: undefined})}/modelsources/git`;
        return this.httpClient.request<Array<GitModel>>('get', `${this.configuration.basePath}${localVarPath}`,
            {
                context: localVarHttpContext,
                responseType: <any>responseType_,
                withCredentials: this.configuration.withCredentials,
                headers: localVarHeaders,
                observe: observe,
                transferCache: localVarTransferCache,
                reportProgress: reportProgress
            }
        );
    }

    /**
     * Get Revisions Of Primary Git Model
     * @param projectSlug 
     * @param modelSlug 
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     */
    public getRevisionsOfPrimaryGitModel(projectSlug: string, modelSlug: string, observe?: 'body', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<GetRevisionsResponseModel>;
    public getRevisionsOfPrimaryGitModel(projectSlug: string, modelSlug: string, observe?: 'response', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<HttpResponse<GetRevisionsResponseModel>>;
    public getRevisionsOfPrimaryGitModel(projectSlug: string, modelSlug: string, observe?: 'events', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<HttpEvent<GetRevisionsResponseModel>>;
    public getRevisionsOfPrimaryGitModel(projectSlug: string, modelSlug: string, observe: any = 'body', reportProgress: boolean = false, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<any> {
        if (projectSlug === null || projectSlug === undefined) {
            throw new Error('Required parameter projectSlug was null or undefined when calling getRevisionsOfPrimaryGitModel.');
        }
        if (modelSlug === null || modelSlug === undefined) {
            throw new Error('Required parameter modelSlug was null or undefined when calling getRevisionsOfPrimaryGitModel.');
        }

        let localVarHeaders = this.defaultHeaders;

        let localVarCredential: string | undefined;
        // authentication (PersonalAccessToken) required
        localVarCredential = this.configuration.lookupCredential('PersonalAccessToken');
        if (localVarCredential) {
            localVarHeaders = localVarHeaders.set('Authorization', 'Basic ' + localVarCredential);
        }

        let localVarHttpHeaderAcceptSelected: string | undefined = options && options.httpHeaderAccept;
        if (localVarHttpHeaderAcceptSelected === undefined) {
            // to determine the Accept header
            const httpHeaderAccepts: string[] = [
                'application/json'
            ];
            localVarHttpHeaderAcceptSelected = this.configuration.selectHeaderAccept(httpHeaderAccepts);
        }
        if (localVarHttpHeaderAcceptSelected !== undefined) {
            localVarHeaders = localVarHeaders.set('Accept', localVarHttpHeaderAcceptSelected);
        }

        let localVarHttpContext: HttpContext | undefined = options && options.context;
        if (localVarHttpContext === undefined) {
            localVarHttpContext = new HttpContext();
        }

        let localVarTransferCache: boolean | undefined = options && options.transferCache;
        if (localVarTransferCache === undefined) {
            localVarTransferCache = true;
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

        let localVarPath = `/api/v1/projects/${this.configuration.encodeParam({name: "projectSlug", value: projectSlug, in: "path", style: "simple", explode: false, dataType: "string", dataFormat: undefined})}/models/${this.configuration.encodeParam({name: "modelSlug", value: modelSlug, in: "path", style: "simple", explode: false, dataType: "string", dataFormat: undefined})}/modelsources/git/primary/revisions`;
        return this.httpClient.request<GetRevisionsResponseModel>('get', `${this.configuration.basePath}${localVarPath}`,
            {
                context: localVarHttpContext,
                responseType: <any>responseType_,
                withCredentials: this.configuration.withCredentials,
                headers: localVarHeaders,
                observe: observe,
                transferCache: localVarTransferCache,
                reportProgress: reportProgress
            }
        );
    }

    /**
     * Get Revisions With Model Credentials
     * @param projectSlug 
     * @param gitModelId 
     * @param modelSlug 
     * @param body 
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     */
    public getRevisionsWithModelCredentials(projectSlug: string, gitModelId: number, modelSlug: string, body: string, observe?: 'body', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<GetRevisionsResponseModel>;
    public getRevisionsWithModelCredentials(projectSlug: string, gitModelId: number, modelSlug: string, body: string, observe?: 'response', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<HttpResponse<GetRevisionsResponseModel>>;
    public getRevisionsWithModelCredentials(projectSlug: string, gitModelId: number, modelSlug: string, body: string, observe?: 'events', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<HttpEvent<GetRevisionsResponseModel>>;
    public getRevisionsWithModelCredentials(projectSlug: string, gitModelId: number, modelSlug: string, body: string, observe: any = 'body', reportProgress: boolean = false, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<any> {
        if (projectSlug === null || projectSlug === undefined) {
            throw new Error('Required parameter projectSlug was null or undefined when calling getRevisionsWithModelCredentials.');
        }
        if (gitModelId === null || gitModelId === undefined) {
            throw new Error('Required parameter gitModelId was null or undefined when calling getRevisionsWithModelCredentials.');
        }
        if (modelSlug === null || modelSlug === undefined) {
            throw new Error('Required parameter modelSlug was null or undefined when calling getRevisionsWithModelCredentials.');
        }
        if (body === null || body === undefined) {
            throw new Error('Required parameter body was null or undefined when calling getRevisionsWithModelCredentials.');
        }

        let localVarHeaders = this.defaultHeaders;

        let localVarCredential: string | undefined;
        // authentication (PersonalAccessToken) required
        localVarCredential = this.configuration.lookupCredential('PersonalAccessToken');
        if (localVarCredential) {
            localVarHeaders = localVarHeaders.set('Authorization', 'Basic ' + localVarCredential);
        }

        let localVarHttpHeaderAcceptSelected: string | undefined = options && options.httpHeaderAccept;
        if (localVarHttpHeaderAcceptSelected === undefined) {
            // to determine the Accept header
            const httpHeaderAccepts: string[] = [
                'application/json'
            ];
            localVarHttpHeaderAcceptSelected = this.configuration.selectHeaderAccept(httpHeaderAccepts);
        }
        if (localVarHttpHeaderAcceptSelected !== undefined) {
            localVarHeaders = localVarHeaders.set('Accept', localVarHttpHeaderAcceptSelected);
        }

        let localVarHttpContext: HttpContext | undefined = options && options.context;
        if (localVarHttpContext === undefined) {
            localVarHttpContext = new HttpContext();
        }

        let localVarTransferCache: boolean | undefined = options && options.transferCache;
        if (localVarTransferCache === undefined) {
            localVarTransferCache = true;
        }


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

        let localVarPath = `/api/v1/projects/${this.configuration.encodeParam({name: "projectSlug", value: projectSlug, in: "path", style: "simple", explode: false, dataType: "string", dataFormat: undefined})}/models/${this.configuration.encodeParam({name: "modelSlug", value: modelSlug, in: "path", style: "simple", explode: false, dataType: "string", dataFormat: undefined})}/modelsources/git/${this.configuration.encodeParam({name: "gitModelId", value: gitModelId, in: "path", style: "simple", explode: false, dataType: "number", dataFormat: undefined})}/revisions`;
        return this.httpClient.request<GetRevisionsResponseModel>('post', `${this.configuration.basePath}${localVarPath}`,
            {
                context: localVarHttpContext,
                body: body,
                responseType: <any>responseType_,
                withCredentials: this.configuration.withCredentials,
                headers: localVarHeaders,
                observe: observe,
                transferCache: localVarTransferCache,
                reportProgress: reportProgress
            }
        );
    }

    /**
     * Update Git Model By Id
     * @param projectSlug 
     * @param gitModelId 
     * @param modelSlug 
     * @param patchGitModel 
     * @param observe set whether or not to return the data Observable as the body, response or events. defaults to returning the body.
     * @param reportProgress flag to report request and response progress.
     */
    public updateGitModelById(projectSlug: string, gitModelId: number, modelSlug: string, patchGitModel: PatchGitModel, observe?: 'body', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<GitModel>;
    public updateGitModelById(projectSlug: string, gitModelId: number, modelSlug: string, patchGitModel: PatchGitModel, observe?: 'response', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<HttpResponse<GitModel>>;
    public updateGitModelById(projectSlug: string, gitModelId: number, modelSlug: string, patchGitModel: PatchGitModel, observe?: 'events', reportProgress?: boolean, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<HttpEvent<GitModel>>;
    public updateGitModelById(projectSlug: string, gitModelId: number, modelSlug: string, patchGitModel: PatchGitModel, observe: any = 'body', reportProgress: boolean = false, options?: {httpHeaderAccept?: 'application/json', context?: HttpContext, transferCache?: boolean}): Observable<any> {
        if (projectSlug === null || projectSlug === undefined) {
            throw new Error('Required parameter projectSlug was null or undefined when calling updateGitModelById.');
        }
        if (gitModelId === null || gitModelId === undefined) {
            throw new Error('Required parameter gitModelId was null or undefined when calling updateGitModelById.');
        }
        if (modelSlug === null || modelSlug === undefined) {
            throw new Error('Required parameter modelSlug was null or undefined when calling updateGitModelById.');
        }
        if (patchGitModel === null || patchGitModel === undefined) {
            throw new Error('Required parameter patchGitModel was null or undefined when calling updateGitModelById.');
        }

        let localVarHeaders = this.defaultHeaders;

        let localVarCredential: string | undefined;
        // authentication (PersonalAccessToken) required
        localVarCredential = this.configuration.lookupCredential('PersonalAccessToken');
        if (localVarCredential) {
            localVarHeaders = localVarHeaders.set('Authorization', 'Basic ' + localVarCredential);
        }

        let localVarHttpHeaderAcceptSelected: string | undefined = options && options.httpHeaderAccept;
        if (localVarHttpHeaderAcceptSelected === undefined) {
            // to determine the Accept header
            const httpHeaderAccepts: string[] = [
                'application/json'
            ];
            localVarHttpHeaderAcceptSelected = this.configuration.selectHeaderAccept(httpHeaderAccepts);
        }
        if (localVarHttpHeaderAcceptSelected !== undefined) {
            localVarHeaders = localVarHeaders.set('Accept', localVarHttpHeaderAcceptSelected);
        }

        let localVarHttpContext: HttpContext | undefined = options && options.context;
        if (localVarHttpContext === undefined) {
            localVarHttpContext = new HttpContext();
        }

        let localVarTransferCache: boolean | undefined = options && options.transferCache;
        if (localVarTransferCache === undefined) {
            localVarTransferCache = true;
        }


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

        let localVarPath = `/api/v1/projects/${this.configuration.encodeParam({name: "projectSlug", value: projectSlug, in: "path", style: "simple", explode: false, dataType: "string", dataFormat: undefined})}/models/${this.configuration.encodeParam({name: "modelSlug", value: modelSlug, in: "path", style: "simple", explode: false, dataType: "string", dataFormat: undefined})}/modelsources/git/${this.configuration.encodeParam({name: "gitModelId", value: gitModelId, in: "path", style: "simple", explode: false, dataType: "number", dataFormat: undefined})}`;
        return this.httpClient.request<GitModel>('put', `${this.configuration.basePath}${localVarPath}`,
            {
                context: localVarHttpContext,
                body: patchGitModel,
                responseType: <any>responseType_,
                withCredentials: this.configuration.withCredentials,
                headers: localVarHeaders,
                observe: observe,
                transferCache: localVarTransferCache,
                reportProgress: reportProgress
            }
        );
    }

}
