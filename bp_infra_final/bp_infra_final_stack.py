from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_cloudwatch as cloudwatch,
    aws_sns as sns,
    aws_cloudwatch_actions as cw_actions
)
from constructs import Construct

class BpInfraFinalStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. Cria uma nova VPC
        vpc = ec2.Vpc(self, "MyVPC",
            max_azs=2
        )
        
        # Cria uma instância EC2 dentro da nova VPC
        ec2_instance = ec2.Instance(self, "MySimpleInstance",
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T2, ec2.InstanceSize.MICRO
            ),
            machine_image=ec2.AmazonLinuxImage(
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2
            ),
            vpc=vpc
        )
        
        # Cria um Security Group para a instância
        sg = ec2.SecurityGroup(self, "MyInstanceSG",
            vpc=vpc,
            description="Allow SSH access to EC2 instance"
        )
        sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(22),
            description="Allow SSH access"
        )

        # 2. Cria um tópico SNS para notificações de alarme
        alarm_topic = sns.Topic(self, "AlarmTopic",
            display_name="EC2 CPU Alarm"
        )
        
        # 3. Cria um alarme do CloudWatch para a CPU da instância
        cpu_alarm = cloudwatch.Alarm(self, "HighCPUAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/EC2",
                metric_name="CPUUtilization",
                dimensions_map={"InstanceId": ec2_instance.instance_id}
            ),
            evaluation_periods=1,
            threshold=50,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            alarm_description="Alarm when CPU exceeds 50%"
        )

        # 4. Conecta o alarme ao tópico SNS
        cpu_alarm.add_alarm_action(cw_actions.SnsAction(alarm_topic))