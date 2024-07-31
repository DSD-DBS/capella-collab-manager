<!--
 ~ SPDX-FileCopyrightText: Copyright DB InfraGO AG and contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Setup Keycloak as Identity Provider

This guide will help you set up [Keycloak](https://www.keycloak.org/) as an
identity provider for _Capella Collaboration Manager (CCM)_. However, it is
important to note that this guide only focuses on setting up the connection
between Keycloak and CCM and does not provide detailed information on how to
set up Keycloak for a production environment.

## Step 1: Install Keycloak

If you don't have a running Keycloak server, please select and follow the
installation instructions in
[Keycloak - Getting Started](https://www.keycloak.org/guides#getting-started).
We will go through the steps and configurations needed in both Keycloak and the
CCM to use Keycloak as an identity provider, but we still recommend that you
carefully read the Keycloak documentation to properly configure your instance.
After this step, you should have access to the Keycloak admin console, which is
required for the following steps. for the following steps.

## Step 2: Create a Capella Collaboration Manager Client in Keycloak

1. Below _Manage_ click on _Clients_
1. Click on _Create client_
1. In the first step, the _General settings_ set the values as follows:
   1. _Client type_: OpenID Connect
   1. _Client ID_: capella-collaboration-manager
   1. _Name_: Capella Collaboration Manager
   1. _Description_: Client used to authenticate users to Capella Collaboration
      Manager
   1. _Allow display in UI_: Own preference
1. In the second step, the _Capability config_ set the values as follows:
   1. Disable _Direct access grants_ since the CCM should not have access to
      the keycloak username or password
   1. Enable _Client Authentication_ because the CCM backend uses the client id
      and client secret to exchange the authorization code retrieved by the
      user after successful authentication to Keycloak for an identity token.
1. In the third step, the _Login settings_ set the values as follows:
   1. _Root URL_: http://localhost:4200
   1. _Home URL_: http://localhost:4200
   1. _Valid redirect URIs_: http://localhost:4200/oauth2/callback
   1. _Valid post logout redirect URIs_: None
   1. _Web origins_: http://localhost:4200
1. Click _Save_, which should create the client in Keycloak
1. Now we just need to make the email claim optional for now, as it is not
   required or used by the CCM, which can be done as follows:
   1. In the Clients tab, click the newly created CCM client
   1. Click on _Client scopes_
   1. For the _email_ scope, change the _Assigned Type_ from _Default_ to
      _Optional_

## Step 3: Configure the CCM to use the Keycloak Client

In the following, we will only consider configurations below _authentication_
or, in the case of the _values.yaml_ file, below _backend.authentication_, so
we will omit these prefixes.

1. Configure the CCM configuration:
   1. Set the _jwt.usernameClaim_ to _preferred_username_, which will be the
      username used in the CCM. You can set this to another field of the
      identity token, but make sure that the field exists and is unique per
      user. For example, we could use the user's email address here, which
      would require you to set this to _email_ and also add the _email_ scope
      below.
   1. Set _endpoints.wellKnown_ to the well-known Keycloak URL, which can be
      found as follows
      1. In Keycloak, click _Realm Settings_
      1. Scroll down and click _OpenID Endpoint Configuration_, which should
         open the configuration in a new tab.
      1. The well-known URL is now simply the URL of the page.
   1. Set the _issuer_ to: http://localhost:8085/realms/master, which is
      typically the well-known URL without the _/.well-known/..._ part.
   1. Set the _scopes_ to _openid_ and _profile_
   1. Set the _client.id_ to the value used when the client was created, so if
      not changed it should be _capella-collaboration-manager_.
   1. Set the _client.secret_ to the client secret which can be found as
      follows:
      1. In Keycloak, click on _Clients_ and then select the CCM client
      1. Click on _Credentials_ (If Credentials is not visible, you have not
         enabled _Client Authentication_, which can be done in the General
         Settings just below _Capability Config_.)
      1. Here you can now copy the _Client Secret_, but be sure to keep this
         value confidential and generate a new client secret in case it gets
         leaked.
   1. Set the _redirectURI_ to the CCM base url + _/oauth2/callback_

The CCM should then be successfully configured and you can run it to verify
that you can authenticate to it using Keycloak.
