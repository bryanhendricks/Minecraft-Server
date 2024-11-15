# AWS Minecraft Server
This repo is used to spin up a Minecraft server in AWS. It uses the [LazyMC Proxy](https://github.com/timvisee/lazymc) running on a small, cheap server to start up and shut down a much larger server based on if players are connected or not, allowing it to shut down the larger server when not in use to save money.

### Custom LazyMC Executable
LazyMC was designed to work with a locally-running Minecraft instance, not a separate server, so I made some terrible ChatGPT-driven changes and compiled a new version that allows LazyMC to handle remote servers. As a result, this executable has only been tested with Minecraft 1.20.1, and is almost guaranteed to not work with any other version.

The changes in question are at https://github.com/bryanhendricks/lazymc_aws/tree/aws, and are based on [LazyMC version 0.2.10](https://github.com/timvisee/lazymc/tree/v0.2.10).

### BetterMC
This repo is specifically designed to spin up an instance of Minecraft using the [Better Minecraft mod pack](https://www.curseforge.com/minecraft/modpacks/better-mc-forge-bmc4). In order to make this modpack work with the AWS infrastructure it's running on, I had to disable the `NoChatReports` mod (no, I don't know why it works when I use EBS, but doesn't work when I use EFS; I suspect witchcraft) - this means than the first time or two that anyone tries to use text chat on the server, it will give them a warning pop-up saying that Microsoft can read your messages. This is the default Minecraft behavior, and is merely a result of clients still having the `NoChatReports` mod installed, while the server does not.

### Yeah cool but like, how do I do the thing?
Go make an AWS account at https://console.aws.amazon.com/. Once you've signed in to the AWS console, choose your region using the dropdown in the top right - just choose the region that's closest to you. Update the `region` field in [cdk.json](cdk.json) with the region you chose, and update the `account` field with your AWS account ID (which you can see in the other dropdown menu in the top right of the AWS Console).

To give yourself admin privileges, get your Minecraft username and your Minecraft UUID (see https://mcuuid.net/ to get your UUID), and enter those into the `admin_username` and `admin_uuid` field in [cdk.json](cdk.json). With that, you can run commands like `/whitelist on` in the Minecraft text chat once you've connected to the server to turn on a server whitelist, then `/whitelist add <USERNAME>` to add people to the whitelist, or you can run any other Operator commands you want.

Next, go to https://console.aws.amazon.com/ec2/home#CreateKeyPair and create a new SSH key. This will allow you to log in to the proxy server or the Minecraft server and fix things if you need to. Just give it a name, and choose `.pem` as the `Private key file format`. 

I recommend using [WSL](https://learn.microsoft.com/en-us/windows/wsl/install) and VSCode if you're on Windows. Once you have that installed, open a VSCode window connected to WSL and install AWS CDK with the instructions [here](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html) (don't forget the `Prerequisites` section - this will walk you through creating an AWS account and installing the dependencies that AWS CDK requires). If you're on Mac, use `brew` or something, idk man.

Once you have AWS CDK installed and authenticated with your AWS account, run `cdk deploy --require-approval=never` at this repo's location, and wait a while. If it breaks, dang. If not, it should give you a proxy IP address, which you can put into your Minecraft server browser. To get the proxy server to start up the Minecraft server, just try to connect to the proxy server, then wait like 10 minutes because Better Minecraft takes forever to start. The Minecraft server will automatically shut down once nobody's been on the server for a few minutes.
