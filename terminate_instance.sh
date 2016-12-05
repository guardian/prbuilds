
set -u
set -e

function killInstance() {

    instance=$(aws ec2 describe-instances --filters Name="tag:Lifetime",Values="Temporary" --profile frontend --region eu-west-1 --query 'Reservations[0].Instances[0].InstanceId')

    stripped=$(echo $instance | sed 's/"//g')

    echo "Killing $stripped. Proceed? [y/n]"
    read yesno

    if [[ "$yesno" == "y" ]]; then
        aws ec2 terminate-instances --instance-ids $stripped --region eu-west-1 --profile frontend
    fi

}

killInstance
