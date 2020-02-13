import boto3


def lambda_handler(event, context):
    client = boto3.client("lambda")

    function_names = [
        "Parqr-ModelTrain",
        "Parser",
        "Parqr-API",
        "Parqr",
        "Feedbacks",
        "Parqr-Cleaner"
    ]

    for function in function_names:
        response = client.update_function_code(
            FunctionName=function,
            S3Bucket="git-to-amazon-s3-outputbucket-7xiedlur8bgn",
            S3Key="tailorck/parqr-flask/merge-branch/tailorck_parqr-flask.zip",
            Publish=True
        )
        version = response.get("Version")
        print("Created new version {} for lambda {}".format(version, function))

        aliases = client.list_aliases(
            FunctionName=function
        ).get("Aliases")

        for alias in aliases:
            if alias.get("Name") == "PROD":
                response = client.update_alias(
                    FunctionName=function,
                    Name='PROD',
                    FunctionVersion=version
                )
                print("Updated alias PROD for function {} with new version {}"
                      .format(function, version))
