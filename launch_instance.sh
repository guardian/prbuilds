
set -u
set -e

function launchInstance() {

    instanceID=$(aws ec2 run-instances --image-id ami-d75f22a4 --security-group-ids sg-d7827eb1 --count 1 --instance-type t2.medium --key-name matthew-walls --subnet-id subnet-c682e7b0 --query 'Instances[0].InstanceId' --profile frontend --region eu-west-1 --iam-instance-profile "Arn=arn:aws:iam::642631414762:instance-profile/lakeboard-stack-InstanceProfile-G2MIRW0FGMVN" --associate-public-ip-address | sed 's/"//')

    echo "Created instance $instanceID"
    
    aws ec2 create-tags --resources $instanceID --tags "Key=Lifetime,Value=Temporary" --profile frontend --region eu-west-1
    
    domain=$(aws ec2 describe-instances --instance-ids $instanceID --profile frontend --region eu-west-1 --query 'Reservations[0].Instances[0].PublicDnsName')
    
    echo $instanceID / $domain

}

launchInstance
