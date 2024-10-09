<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Uninstallation of the Collaboration Manager

We're sorry to see you go :sob: <br /> If you have any suggestions for us to
improve, please share them with us. Either privately via <set@deutschebahn.com>
or via a
[GitHub issue](https://github.com/DSD-DBS/capella-collab-manager/issues).

1.  If you want to uninstall the management portal, you can run the following
    comment:

    ```zsh
    helm uninstall <release-name> -n <namespace> helm
    ```

    or delete the management portal namespace:

    ```zsh
    kubectl delete namespace <namespace>
    ```

1.  The previous command doesn't clean the sessions namespace. Please clean it
    manually by running (this does also remove all persistent workspaces!):

    ```zsh
    kubectl -n <sessions-namespace> delete all --all
    ```

    or just delete the namespace:

    ```zsh
    kubectl delete namespace <sessions-namespace>
    ```
