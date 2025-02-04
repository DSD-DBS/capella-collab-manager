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



export interface CPUResourcesOutput { 
    /**
     * Each session gets at least the specified amount of physical or virtual CPU cores. An inaccurate value can lead to higher costs. To find the right value, you can use the Kubernetes dashboard to monitor the resource usage of the tool. Refer to the Kubernetes documentation for more details: https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/#requests-and-limits
     */
    requests: number;
    /**
     * Each session can not consume more than the specified amount of physical or virtual CPU cores. A high value can lead to high costs, while a low value can lead to performance issues. To find the right value, you can use the Kubernetes dashboard to monitor the resource usage of the tool. Refer to the Kubernetes documentation for more details: https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/#requests-and-limits
     */
    limits: number;
}

