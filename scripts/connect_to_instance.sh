
set -u
set -e

function connectToInstance() {

    domain=$(aws ec2 describe-instances --filters Name="tag:Lifetime",Values="Temporary" --profile frontend --region eu-west-1 --query 'Reservations[0].Instances[0].PublicDnsName')

    stripped=$(echo $domain | sed 's/"//g')

    echo "Connecting to $domain"
    ssh -i ~/Downloads/matthew-walls.pem "ubuntu@$stripped"

}

connectToInstance
