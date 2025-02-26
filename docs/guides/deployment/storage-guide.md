---
description: Store your flow code
tags:
    - guides
    - guide
    - flow code
    - storage
    - code storage
    - repository
    - github
    - git
    - gitlab
    - bitbucket
    - s3
    - azure
    - blob storage
    - bucket
    - AWS
    - GCP
    - GCS
    - Google Cloud Storage
    - Azure Blob Storage
    - Docker
    - storage  
search:
  boost: 2
---

# Where to Store Your Flow Code

When a flow runs, the execution environment needs access to its code. 
Flow code is not stored in a Prefect server database instance or Prefect Cloud. 
When deploying a flow, you have several flow code storage options.

## Option 1: Local storage

Local flow code storage is often used with a Local Subprocess work pool for initial experimentation. 

To create a deployment with local storage and a Local Subprocess work pool, do the following:

1. Run `prefect deploy` from the root of the directory containing your flow code.
1. Select that you want to create a new deployment, select the flow code entrypoint, and name your deployment. 
1. Select a *process* work pool. 

You are then shown the location that your flow code will be fetched from when a flow is run. 
For example:

<div class="terminal">
```bash
Your Prefect workers will attempt to load your flow from: 
/my-path/my-flow-file.py. To see more options for managing your flow's code, run:

    $ prefect init
```
</div>

When deploying a flow to production, you most likely want code to run with infrastructure-specific configuration. 
The flow code storage options shown below are recommended for production deployments.

## Option 2: Git-based storage

Git-based version control platforms are popular locations for code storage. 
They provide redundancy, version control, and easier collaboration.

[GitHub](https://github.com/) is the most popular cloud-based repository hosting provider. 
[GitLab](https://www.gitlab.com) and [Bitbucket](https://bitbucket.org/) are other popular options. 
Prefect supports each of these platforms.

### Creating a deployment with git-based storage

Run `prefect deploy` from within a git repository and create a new deployment. You will see a series of prompts. Select that you want to create a new deployment, select the flow code entrypoint, and name your deployment.

Prefect detects that you are in a git repository and asks if you want to store your flow code in a git repository. Select "y" and you will be prompted to confirm the URL of your git repository and the branch name, as in the example below:

<div class="terminal">
```bash
? Your Prefect workers will need access to this flow's code in order to run it. 
Would you like your workers to pull your flow code from its remote repository when running this flow? [y/n] (y): 
? Is https://github.com/my_username/my_repo.git the correct URL to pull your flow code from? [y/n] (y): 
? Is main the correct branch to pull your flow code from? [y/n] (y): 
? Is this a private repository? [y/n]: y
```
</div>

In this example, the git repository is hosted on GitHub. 
If you are using Bitbucket or GitLab, the URL will match your provider.
If the repository is public, enter "n" and you are on your way.

If the repository is private, you can enter a token to access your private repository. This token will be saved in an encrypted Prefect Secret block. 

<div class="terminal">
```bash

? Please enter a token that can be used to access your private repository. This token will be saved as a Secret block via the Prefect API: "123_abc_this_is_my_token"
```
</div>

Verify that you have a new Secret block in your active workspace named in the format "deployment-my-deployment-my-flow-name-repo-token".

Creating access tokens differs for each provider.

=== "GitHub" 

    We recommend using HTTPS with [fine-grained Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token) so that you can limit access by repository. 
    See the GitHub docs for [Personal Access Tokens (PATs)](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token).

    Under *Your Profile->Developer Settings->Personal access tokens->Fine-grained token* choose *Generate New Token* and fill in the required fields. 
    Under *Repository access* choose *Only select repositories* and grant the token permissions for *Contents*.

=== "Bitbucket"

    We recommend using HTTPS with Repository, Project, or Workspace [Access Tokens](https://support.atlassian.com/bitbucket-cloud/docs/access-tokens/). 
    
    You can create a Repository Access Token with Scopes->Repositories->Read.

    Bitbucket requires you prepend the token string with `x-token-auth:` So the full string looks like `x-token-auth:abc_123_this_is_my_token`. 

=== "GitLab"

    We recommend using HTTPS with [Project Access Tokens](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html).

    In your repository in the GitLab UI, select *Settings->Repository->Project Access Tokens* and check *read_repository* under *Select scopes*.

If you want to configure a Secret block ahead of time for use when deploying a `prefect.yaml` file, create the block via code or the Prefect UI and reference it like this:

```yaml

pull:
    - prefect.deployments.steps.git_clone:
        repository: https://bitbucket.org/org/my-private-repo.git
        access_token: "{{ prefect.blocks.secret.my-block-name }}"
```

Alternatively, you can create a Credentials block ahead of time and reference it in the `prefect.yaml` pull step.

=== "GitHub"

    1. Install the Prefect-Github library with `pip install -U prefect-github`
    1. Register the blocks in that library to make them available on the server with `prefect block register -m prefect_github`.
    1. Create a GitHub Credentials block via code or the Prefect UI and reference it as shown above.
    1. In addition to the block name, most users will need to fill in the *GitHub Username* and *GitHub Personal Access Token* fields.

    ```yaml

    pull:
        - prefect.deployments.steps.git_clone:
            repository: https://github.com/discdiver/my-private-repo.git
            credentials: "{{ prefect.blocks.github-credentials.my-block-name }}"
    ```
  
=== "Bitbucket"
    
    1. Install the relevant library with `pip install -U prefect-bitbucket`
    1. Register the blocks in that library with `prefect block register -m prefect_bitbucket` 
    1. Create a Bitbucket credentials block via code or the Prefect UI and reference it as shown above.
    1. In addition to the block name, most users will need to fill in the *Bitbucket Username* and *Bitbucket Personal Access Token* fields.

    ```yaml

    pull:
        - prefect.deployments.steps.git_clone:
            repository: https://bitbucket.org/org/my-private-repo.git
            credentials: "{{ prefect.blocks.bitbucket-credentials.my-block-name }}"
    ```

=== "GitLab"
    
    1. Install the relevant library with `pip install -U prefect-gitlab`
    1. Register the blocks in that library with `prefect block register -m prefect_gitlab` 
    1. Create a GitLab credentials block via code or the Prefect UI and reference it as shown above.
    1. In addition to the block name, most users will need to fill in the *GitLab Username* and *GitLab Personal Access Token* fields.

    ```yaml

    pull:
        - prefect.deployments.steps.git_clone:
            repository: https://gitlab.com/org/my-private-repo.git
            credentials: "{{ prefect.blocks.gitlab-credentials.my-block-name }}"
    ```

!!! warning "Push your code"
    When you make a change to your code, Prefect does not push your code to your git-based version control platform. 
    You need to push your code manually or as part of your CI/CD pipeline. 
    This design decision is an intentional one to avoid confusion about the git history and push process.

## Option 3: Docker-based storage

Another popular way to store your flow code is to include it in a Docker image. The following work pools use Docker containers, so the flow code can be directly baked into the image:

- Docker
- Kubernetes
- Serverless cloud-based options
    - AWS Elastic Container Service 
    - Azure Container Instances
    - Google Cloud Run
- Push-based serverless cloud-based options (no worker required)
    - AWS Elastic Container Service - Push
    - Azure Container Instances - Push
    - Google Cloud Run - Push

1. Run `prefect init` in the root of your repository and choose `docker` for the project name and answer the prompts to create a `prefect.yaml` file with a build step that will create a Docker image with the flow code built in. See the [Workers and Work Pools page of the tutorial](/tutorial/workers/) for more info.
1. Run `prefect deploy` to create a deployment. 
1. Upon deployment run the worker will pull the Docker image and spin up a container. 
1. The flow code baked into the image will run inside the container. 

!!! tip "CI/CD may not require push or pull steps"
    You don't need push or pull steps in the `prefect.yaml` file if using CI/CD to build a Docker image outside of Prefect. 
    Instead, the work pool can reference the image directly.

## Option 4: Cloud-provider storage

You can store your code in an AWS S3 bucket, Azure Blob Storage container, or GCP GCS bucket and specify the destination directly in the `push` and `pull` steps of your `prefect.yaml` file.

To create a templated `prefect.yaml` file run `prefect init` and select the recipe for the applicable cloud-provider storage.
Below are the recipe options and the relevant portions of the `prefect.yaml` file.

=== "AWS S3 bucket"

    Choose `s3` as the recipe and enter the bucket name when prompted.

    ```yaml

    # push section allows you to manage if and how this project is uploaded to remote locations
    push:
    - prefect_aws.deployments.steps.push_to_s3:
        id: push_code
        requires: prefect-aws>=0.3.4
        bucket: my-bucket
        folder: my-folder
        credentials: "{{ prefect.blocks.aws-credentials.my-credentials-block }}" # if private

    # pull section allows you to provide instructions for cloning this project in remote locations
    pull:
    - prefect_aws.deployments.steps.pull_from_s3:
        id: pull_code
        requires: prefect-aws>=0.3.4
        bucket: '{{ push_code.bucket }}'
        folder: '{{ push_code.folder }}'
        credentials: "{{ prefect.blocks.aws-credentials.my-credentials-block }}" # if private 
    ``` 

    If the bucket requires authentication to access it, you can do the following:

    1. Install the [Prefect-AWS](https://prefecthq.github.io/prefect-aws/) library with `pip install -U prefect-aws`
    1. Register the blocks in Prefect-AWS with `prefect block register -m prefect_aws` 
    1. Create a user with a role with read and write permissions to access the bucket. If using the UI, create an access key pair with *IAM->Users->Security credentials->Access keys->Create access key*. Choose *Use case->Other* and then copy the *Access key* and *Secret access key* values.
    1. Create an AWS Credentials block via code or the Prefect UI. In addition to the block name, most users will fill in the *AWS Access Key ID* and *AWS Access Key Secret* fields.
    1. Reference the block as shown in the push and pull steps above. 
    
=== "Azure Blob Storage container"

    Choose `azure` as the recipe and enter the container name when prompted.

    ```yaml
    
    # push section allows you to manage if and how this project is uploaded to remote locations
    push:
    - prefect_azure.deployments.steps.push_to_azure_blob_storage:
        id: push_code
        requires: prefect-azure>=0.2.8
        container: my-prefect-azure-container
        folder: my-folder
        credentials: "{{ prefect.blocks.azure-blob-storage-credentials.my-credentials-block }}" # if private

    # pull section allows you to provide instructions for cloning this project in remote locations
    pull:
    - prefect_azure.deployments.steps.pull_from_azure_blob_storage:
        id: pull_code
        requires: prefect-azure>=0.2.8
        container: '{{ push_code.container }}'
        folder: '{{ push_code.folder }}'
        credentials: "{{ prefect.blocks.azure-blob-storage-credentials.my-credentials-block }}" # if private
    ```

    If the blob requires authentication to access it, you can do the following:

    1. Install the [Prefect-Azure](https://prefecthq.github.io/prefect-azure/) library with `pip install -U prefect-azure`
    1. Register the blocks in Prefect-Azure with `prefect block register -m prefect_azure` 
    1. Create an access key for a role with sufficient (read and write) permissions to access the blob. A connection string that will contain all needed information can be created in the UI under *Storage Account->Access keys*.
    1. Create an Azure Blob Storage Credentials block via code or the Prefect UI. Enter a name for the block and paste the connection string into the *Connection String* field.
    1. Reference the block as shown in the push and pull steps above. 

=== "GCP GCS bucket"

    Choose `gcs`` as the recipe and enter the bucket name when prompted.

    ```yaml

    # push section allows you to manage if and how this project is uploaded to remote locations
    push:
    - prefect_gcp.deployment.steps.push_to_gcs:
        id: push_code
        requires: prefect-gcp>=0.4.3
        bucket: my-bucket
        folder: my-folder
        credentials: "{{ prefect.blocks.gcp-credentials.my-credentials-block }}" # if private 

    # pull section allows you to provide instructions for cloning this project in remote locations
    pull:
    - prefect_gcp.deployment.steps.pull_from_gcs:
        id: pull_code
        requires: prefect-gcp>=0.4.3
        bucket: '{{ push_code.bucket }}'
        folder: '{{ pull_code.folder }}'
        credentials: "{{ prefect.blocks.gcp-credentials.my-credentials-block }}" # if private 
    ```
    
    If the bucket requires authentication to access it, you can do the following:

    1. Install the [Prefect-GCP](https://prefecthq.github.io/prefect-azure/) library with `pip install -U prefect-gcp`
    1. Register the blocks in Prefect-GCP with `prefect block register -m prefect_gcp` 
    1. Create a service account in GCP for a role with read and write permissions to access the bucket contents. If using the GCP 
    console, go to *IAM & Admin->Service accounts->Create service account*. After choosing a role with the required permissions, see your service account and click on the three dot menu in the *Actions* column. Select *Manage Keys->ADD KEY->Create new key->JSON*. Download the JSON file.
    1. Create a GCP Credentials block via code or the Prefect UI. Enter a name for the block and paste the entire contents of the JSON key file into the *Service Account Info* field.
    1. Reference the block as shown in the push and pull steps above. 

Another option for authentication is for the [worker](/concepts/work-pools/#worker-overview) to have access to the the storage location at runtime via SSH keys.

Alternatively, you can inject environment variables into your deployment like this example that uses an environment variable named `CUSTOM_FOLDER`:

```yaml

 push:
    - prefect_gcp.deployment.steps.push_to_gcs:
        id: push_code
        requires: prefect-gcp>=0.4.3
        bucket: my-bucket
        folder: '{{ $CUSTOM_FOLDER }}'
```

## Including and excluding files from storage

By default, Prefect uploads all files in the current folder to the configured storage location when you create a deployment.

When using a git repository, Docker image, or cloud-provider storage location, you may want to exclude certain files or directories.
- If you are familiar with git you are likely familiar with the [`.gitignore`](https://git-scm.com/docs/gitignore) file. 
- If you are familiar with Docker you are likely familiar with the [`.dockerignore`](https://docs.docker.com/engine/reference/builder/#dockerignore-file) file. 
- For cloud-provider storage the `.prefectignore` file serves the same purpose and follows a similar syntax as those files. So an entry of `*.pyc` will exclude all `.pyc` files from upload.

## Other code storage creation methods

In earlier versions of Prefect [storage blocks](/concepts/blocks/) were the recommended way to store flow code. 
Storage blocks are still supported, but not recommended.

As shown above, repositories can be referenced directly through interactive prompts with `prefect deploy` or in a `prefect.yaml`. 
When authentication is needed, Secret or Credential blocks can be referenced, and in some cases created automatically through interactive deployment creation prompts. 

## Next steps

You've seen options for where to store your flow code. 

We recommend using Docker-based storage or git-based storage for your production deployments.

Check out more [guides](/guides/) to reach your goals with Prefect.
