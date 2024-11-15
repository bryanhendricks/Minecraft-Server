from aws_cdk import App, Environment
from minecraft_server_stack import MinecraftServerStack

app = App(context={"env": "default"})
conf = app.node.try_get_context("environments")[app.node.try_get_context("env")]
env = Environment(account=conf["account"], region=conf["region"])
MinecraftServerStack(app, conf["stack_name"], conf, env=env)
app.synth()
