<!--
 ~ SPDX-FileCopyrightText: Copyright DB Netz AG and the capella-collab-manager contributors
 ~ SPDX-License-Identifier: Apache-2.0
 -->

# Browse, upload and download files

<!-- prettier-ignore-start -->

1. Navigate to the `Session` tab.
1. On the right side, select the corresponding session. Select the persistent
   session to upload files into your persistent workspace. Click the
   `File browser` button:

    ![File browser button](file-browser-button.png){:style="width:400px"}

1. Wait until the file-tree has loaded.

    ![File browser dialog](upload-dialog.png){:style="width:300px"}

    !!! info
         Hidden directories (e.g., the `.metadata` directory) are not
         visible by default. You can make them visible by clicking on
         the `Show hidden files` checkbox.

1. You can expand the directories by clicking on the "directory" icon:

    ![Expand directory in file browser](expand-directory.png){:style="width:300px"}

=== "Upload files"

    !!! info
            It is currently only possible to upload files with a file size of less than 30MB.
            For larger files we recommend a data transfer via Git.

      1. Click the `Upload` button on the directory you want to place the file in.

          ![Upload files button](upload-files-button.png){:style="width:300px"}

      1. Now, select the file(s) to upload and confirm. The files to be uploaded are marked in green.

         ![List of files to upload](files-to-upload.png)

      1. When you're ready and selected all files to upload, confirm your
         selection with `Submit`.
      1. The upload can take a few seconds/minutes, depending on the file size.
      1. When the upload was successful, the dialog closes without error message.

=== "Download files"

   Documentation for "Download files" will follow soon.

<!-- prettier-ignore-end -->
