<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Installation of the Collaboration Manager

This guide will help you set up the Capella Collaboration Manager on a
Kubernetes cluster. The setup of the basic installation is straightforward, but
we'll also delve into the more complex TeamForCapella support that requires
building custom Docker images.

During development, we also took into account that the application can be
installed in highly restricted environments. An internet connection is not
necessarily required.

## Step 1: Set up a Kubernetes cluster

Kubernetes allows us to make operations as simple as possible later on. Updates
can be fully automated. In addition, Kubernetes allows us to ensure a secure
operation through standardized security hardening.

You can use an existing cloud service to create a Kubernetes cluster. We have
running production deployments on Microsoft AKS and Amazon EKS. The application
is designed in such a way that no cluster scope is necessary. All operations
run at the namespace level, so it even runs in shared OpenShift clusters. But
also if you simply have a Linux server at your disposal, this is no obstacle.

If you already have a running cluster, have `kubectl` up and running and can
reach the cluster, then you can skip this step.

We provide instructions for some environments. If you set up the application in
a different environment, please document the installation and obstacles that
you find and we would be happy to receive a PR to help other users in the
future.

=== "microK8s"

    !!! info
        We have tested the instructions with Ubuntu Server 22.04.

    1. Run steps 1-4 of the official microK8s [`Getting started`](https://microk8s.io/docs/getting-started) guide.

    2. Enable all required add-ons:
        ```zsh
        microk8s enable hostpath-storage # For persistent storage
        microk8s enable rbac # For role-based access control
        microk8s enable ingress # For load balancing
        ```
    3. If you don't have any external registry available and TeamForCapella support is required, enable the registry:
        ```zsh
        microk8s enable registry
        export DOCKER_REGISTRY=localhost:32000
        ```
    4. Copy the `kubectl` configuration to the host, so that `helm` can pick it up:
        ```zsh
        mkdir -p $HOME/.kube
        microk8s config > $HOME/.kube/config
        chmod 600 $HOME/.kube/config # Nobody else should be able to read the configuration
        ```
    5. Optional, but recommended: Set up a NFS for workspaces and Juypter file-shares.
        The default `hostpath-storage` of microK8S doesn't enforce the specified capacity on PVCs.
        This can be exploited by a user uploading so much data to their workspace that
        the server goes out of disk storage.

        Please follow the official instructions: <https://microk8s.io/docs/nfs>.

        Make sure to update the `backend.storageClassName` in the `values.yaml` in step 6 to `nfs-csi`.
        All new Jupyter file-shares and personal workspaces will use the new storage class then.

        !!! warning "User mapping for non-root containers"
            If you want to run the session containers as non-root, you can set the `runAsUser` value in the `podSecurityContext` of the values.yaml.
            In the default configuration, `runAsUser` is set to `1004370000`.

            Unfortunately our setup NFS does not respect the `fsGroup` option. Therefore, all volumes are mounted with `nobody:nogroup` per default.
            This will lead to permission errors and crashing session containers.

            To fix it, change the `/etc/exports` file and modify the options for the create file-share to:
            ```
            (rw,sync,no_subtree_check,all_squash,anonuid=<user-id-of-session-containers>,anongid=0)
            ```

            Replace `<user-id-of-session-containers>` with the value of the `runAsUser` value of the Kubernetes Pod security context.

            Then, apply the new configuration by running `exportfs -ra`.

=== "k3d"

    We are constantly working on expanding our documentation. This installation method is currently not documented. If it is relevant, please feel free to contact us at set@deutschebahn.com or open an issue in this repository.

=== "OpenShift"

    We are constantly working on expanding our documentation. This installation method is currently not documented. If it is relevant, please feel free to contact us at set@deutschebahn.com  or open an issue in this repository.

## Step 2: Validate the available resources

The minimum required resources are 3
[Kubernetes CPU cores](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/#meaning-of-cpu)
and around 2,5GiB of memory for the management platform. Depending on the load,
the instance can scale up and is limited to 10 Kubernetes CPU cores cores and
~8GiB of memory.

Each session requires a minimum of 0.4 Kubernetes CPU cores and 1.6Gi of
memory. A session can scale up until it reaches 2 Kubernetes CPU cores and 6Gi
of memory.

## Step 3: Set up the required namespaces (optional)

The Collaboration Manager requires two different namespaces. For security and
overview reasons, they are separated:

<!-- prettier-ignore -->
- Capella Collaboration Manager control namespace: In this namespace, we run
  the core application. It has full control over the sessions namespace and  consists of the following services:
    - Frontend
    - Backend
    - Documentation
    - Guacamole
    - Prometheus
    - Grafana (Loki), can be disabled in the `values.yaml`

- Sessions namespace. The namespace is controlled by the control namespace and you won't need to touch it. In the session namespace, the following services run:
    - Storage for persistent workspaces
    - Storage for Juypter file-shares
    - Pipeline jobs for nightly TeamForCapella to Git synchronisation
    - Session containers (Capella, Papyrus, Juypter, pure::variants)

<!-- prettier-ignore -->
1. Create the two required namespaces:

    ```zsh
    kubectl create namespace collab-manager # If you use another name, please update the following commands and use your namespace name.
    kubectl create namespace collab-sessions # If you use another name, please update the `values.yaml` accordingly.
    ```

2. Set the `collab-manager` as default namespace in the default context (optional):

    ```zsh
    kubectl config set-context --current --namespace=collab-manager
    ```

## Step 4: Install helm

Follow the official instructions to install Helm:
[Installing helm](https://helm.sh/docs/intro/install/)

Verify that `helm` is working by executing the command:

```zsh
helm version
```

## Step 5: Clone the Github repository

Navigate to a persistent location on your server, e.g. `/opt`. Then clone the
Github repository by running:

```zsh
git clone https://github.com/DSD-DBS/capella-collab-manager.git
```

## Step 6: Configure the environment / Create the `values.yaml`

Copy the
[`values.yaml`](https://github.com/DSD-DBS/capella-collab-manager/blob/main/helm/values.yaml)
to a persistent and secure location on your server or deployment environment.
The `local` directory in the Collaboration Manager is gitignored. We recommend
to put the custom `values.yaml` in this directory.

Make sure to set restrictive permissions on the `values.yaml`:

```zsh
chmod 600 values.yaml
```

Adjust all values according to your needs.

## Step 7: Install the application in the cluster

Run the following commands in the root directory of the repository:

```zsh
helm dependency update ./helm
helm upgrade --install \
    --namespace collab-manager \
    --values <path-to-your-custom-values.yaml> \
    <release-name> \
    ./helm
```

## Step 8: Initialize the Guacamole database

The Guacamole database is not initialized automatically. Run the following
command to initialize the PostgreSQL database:

```zsh
kubectl exec --container <release-name>-guacamole-guacamole deployment/<release-name>-guacamole-guacamole -- /opt/guacamole/bin/initdb.sh --postgresql | \
    kubectl exec -i deployment/<release-name>-guacamole-postgres -- psql -U guacamole guacamole
```

After the initialization, the Guacamole password defaults to `guacadmin`. We
have to change it to a more secure password:

1. Open <http://localhost:8080/guacamole/> and login with `guacadmin` /
   `guacadmin`.
1. Click on the `guacadmin` user at the top-right corner of the screen, then
   select "Settings".
1. Select the tab "Preferences"
1. In the "Change password" section, enter `guacadmin` as current password.
   Generate a secure password and enter it for "New password" and confirm it.
   Then, click "Update password"
1. Log out and verify that the combination `guacadmin` / `guacadmin` no longer
   works.
1. Update the key `guacamole.password` in the `values.yaml` and repeat step 7.

## Step 9: Check the application status

Run `kubectl get pods` to see the status of all components. Once all containers
are running, verify the installation state by running:

```zsh
curl http://localhost/api/v1/health/general
```

It should return the following JSON:

```json
{ "guacamole": true, "database": true, "operator": true }
```

If a value is false, check the backend logs for more information.

## Step 10: Add TeamForCapella support

<!-- prettier-ignore -->
!!! info "TeamForCapella server required"
    The setup of the TeamForCapella server and license server itself will
    not be part of this tutorial. To process, you'll need to have a running and
    reachable TeamForCapella server.

<!-- prettier-ignore -->
!!! info "Container registry required"
    For the TeamForCapella support, you'll need to build own Docker images. In order to use this in the cluster, an external or internal container registry is required.

<!-- prettier-ignore -->
1. Install [GNU make](https://www.gnu.org/software/make/manual/make.html) >=
   3.82
1. Navigate to the root of the capella-collab-manager repository.
1. Clone the capella-dockerimages repository:
   ```zsh
   git clone https://github.com/DSD-DBS/capella-dockerimages
   ```
1. Prepare the `capella/base` and `t4c/client/base` images according to the
   Capella Docker images documentation (Only the preparation section is
   needed):

    - [`capella/base`](https://dsd-dbs.github.io/capella-dockerimages/capella/base/#preparation)
    - [`t4c/client/base`](https://dsd-dbs.github.io/capella-dockerimages/capella/t4c/base/#preparation)

1. Set the following environment variables:

    ```zsh
    export PUSH_IMAGES=1 # Auto-push images to the container registry after build
    export DOCKER_REGISTRY=<your-registry> # Location of your remote or local container registry
    export CAPELLA_BUILD_TYPE=offline # Don't download Capella during each build
    export CAPELLA_VERSIONS="5.2.0 6.0.0 6.1.0" # Space separated list of Capella versions to build
    export CAPELLA_DROPINS="" # Command separated list of dropins
    ```

1. Then, build the `t4c/client/remote` images (the one that we'll use in the
   Collaboration Manager):

    ```zsh
    make t4c/client/remote
    ```

1. In the Collaboration Manager UI, navigate to "Menu" > "Settings" > "Tools",
    select the tool and modify the "persistent workspace" image to
   `<registry>/t4c/client/remote:<capella-version>-latest`.
   In addition, enable the TeamForCapella integration by ticking the checkbox: `This tool is used with a TeamForCapella integration`.
