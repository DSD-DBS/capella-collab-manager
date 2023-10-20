<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

## Naming Conventions

### Crud Functions

#### Creating resource

For creating a resource one should use `create` as a prefix followed by the
resource one wants to create (e.g., `createProject(...): Observable<Project>`)

#### Retriving resources

In general, one should use `get` as prefix for a function that retrieves and
returns resources. In case, one wants to get a list of alls resources use
`get + <resource type> + s` as function name (e.g., `getProjects`). In case,
one wants to get a specific resource use
`get + <resource type> + By + <property>` as function name (e.g.,
`getProjectByName(name: string)`). The only exception to this rule is the case
where one wants to get a resource by its identifier where the `By + <property>`
part can be omitted (e.g., `getProject(id: number)`).

In some services, we use the concept of having a static representation of a
resource or a list of resources as observable inside the service. For example,

```ts
private _gitModel = new BehaviorSubject<GetGitModel | undefined>(undefined);
private _gitModels = new BehaviorSubject<GetGitModel[] | undefined>(undefined);

readonly gitModel = this._gitModel.asObservable();
readonly gitModels = this._gitModels.asObservable();
```

In this case, we use the prefix `load` to retrieve the data but instead of
returning it the data is published to all subscribers. However, the naming
rules from above also apply here (e.g., `loadGitModels` to publish all git
models to the `gitModels` observable and `loadGitModelById` to publish only one
git model to the `gitModel` observable)
