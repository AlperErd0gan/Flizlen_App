# ☁️ AWS Free Tier Deployment Guide

Follow these steps to deploy your app to Amazon Web Services (AWS) using the "Free Tier" (t2.micro).

## Prerequisites
1.  **AWS Account**: You must have an active AWS account.
2.  **Key Pair**: You need an EC2 Key Pair to SSH into the server.
    *   Go to **EC2 Dashboard** -> **Key Pairs** -> **Create key pair**.
    *   Name it `flizlen-key`.
    *   Format: `.pem` (for Mac/Linux).
    *   **Save the downloaded file!** (e.g., to `~/Downloads/flizlen-key.pem`).

## 1. Create the Stack (Infrastructure)
1.  Log in to the **AWS Console**.
2.  Search for **CloudFormation**.
3.  Click **Create stack** -> **With new resources (standard)**.
4.  **Prerequisite - Prepare template**: Choose **Template is ready**.
5.  **Specify template**: Choose **Upload a template file**.
6.  Upload the file `flizlen-aws.yaml` (it's in your project folder).
7.  Click **Next**.
8.  **Stack name**: Enter `flizlen-stack`.
9.  **Parameters (KeyName)**: Select the key pair you created (`flizlen-key`).
10. Click **Next** -> **Next** -> **Submit**.

## 2. Get Your Server IP
1.  Wait for the stack status to turn **CREATE_COMPLETE** (approx. 2-3 mins).
2.  Click the **Outputs** tab.
3.  Copy the **PublicIP** (e.g., `54.123.45.67`).

## 3. Connect & Deploy
Open your terminal on your Mac.

1.  **Secure your key** (only needed once):
    ```bash
    chmod 400 ~/Downloads/flizlen-key.pem
    ```
2.  **SSH into the server**:
    ```bash
    ssh -i ~/Downloads/flizlen-key.pem ubuntu@<YOUR_PUBLIC_IP>
    ```
    *(Note: user is `ubuntu`, not `root`)*

3.  **Clone & Run Setup**:
    ```bash
    git clone <YOUR_GITHUB_REPO_URL> flizlen
    cd flizlen
    chmod +x setup_vps.sh
    
    # Run setup (use sudo because you are 'ubuntu' user)
    sudo ./setup_vps.sh <YOUR_PUBLIC_IP>
    ```

## 4. Done!
Access your app at `http://<YOUR_PUBLIC_IP>`.

## ⚠️ Important AWS Notes
1.  **Stop vs Terminate**: If you want to pause billing/usage, **Stop** the instance in EC2 console. If you **Terminate** it (or delete the CloudFormation stack), the server and all data are deleted 4ever.
2.  **Memory**: This is a `t2.micro` (1GB RAM). If the app crashes with 40 users, you may need to manually upgrade execution instance type to `t3.medium` (Paid) in the EC2 Console for the demo day.
