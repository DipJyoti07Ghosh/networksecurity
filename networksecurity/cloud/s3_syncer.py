
import os


class S3Sync:
    def sync_folder_to_s3(self, folder, aws_bucket_url):
        command = f"aws s3 sync {folder} {aws_bucket_url}"
        print(f"EXECUTING COMMAND: {command}")
        result = os.system(command)
        print(f"COMMAND EXIT CODE: {result}") # Exit code 0 means success

    def sync_folder_from_s3(self,folder,aws_bucket_url):
        command = f"aws s3 sync  {aws_bucket_url} {folder} "
        os.system(command)
