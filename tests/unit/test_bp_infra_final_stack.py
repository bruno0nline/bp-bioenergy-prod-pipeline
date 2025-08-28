import aws_cdk as core
import aws_cdk.assertions as assertions

from bp_infra_final.bp_infra_final_stack import BpInfraFinalStack

# example tests. To run these tests, uncomment this file along with the example
# resource in bp_infra_final/bp_infra_final_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = BpInfraFinalStack(app, "bp-infra-final")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
