"""S3 client wrapper — read-only operations."""

import os
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, NoCredentialsError

_client = None


def get_client():
    """Get or create the S3 client (singleton)."""
    global _client
    if _client is not None:
        return _client

    endpoint = os.environ.get("S3_ENDPOINT", "")
    access_key = os.environ.get("S3_ACCESS_KEY", "")
    secret_key = os.environ.get("S3_SECRET_KEY", "")
    region = os.environ.get("S3_REGION", "us-east-1")
    verify_ssl = os.environ.get("S3_VERIFY_SSL", "true").lower() == "true"

    # Determine SSL verify value for boto3
    if not verify_ssl:
        verify = False
    elif os.environ.get("AWS_CA_BUNDLE"):
        verify = os.environ["AWS_CA_BUNDLE"]
    elif os.path.exists("/ssl/fullchain.pem"):
        verify = "/ssl/fullchain.pem"
    else:
        verify = True

    _client = boto3.client(
        service_name="s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region,
        verify=verify,
        config=Config(
            signature_version="s3v4",
            s3={"addressing_style": "path"},
            retries={"max_attempts": 2, "mode": "standard"},
        ),
    )
    return _client


def reset_client():
    """Force client recreation (after config change)."""
    global _client
    _client = None


def list_buckets():
    """List all accessible buckets."""
    try:
        s3 = get_client()
        resp = s3.list_buckets()
        buckets = []
        for b in resp.get("Buckets", []):
            buckets.append({
                "name": b["Name"],
                "created": b["CreationDate"].isoformat() if b.get("CreationDate") else None,
            })
        return {"buckets": buckets, "error": None}
    except (ClientError, NoCredentialsError) as e:
        return {"buckets": [], "error": str(e)}
    except Exception as e:
        return {"buckets": [], "error": str(e)}


def list_objects(bucket, prefix="", delimiter="/", max_keys=200, continuation_token=None):
    """List a single page of objects and prefixes at a given path."""
    try:
        s3 = get_client()
        params = {
            "Bucket": bucket,
            "Prefix": prefix,
            "Delimiter": delimiter,
            "MaxKeys": max_keys,
        }

        if continuation_token:
            params["ContinuationToken"] = continuation_token

        resp = s3.list_objects_v2(**params)

        folders = []
        for p in resp.get("CommonPrefixes", []):
            folder_name = p["Prefix"][len(prefix):]
            folders.append({
                "name": folder_name.rstrip("/"),
                "prefix": p["Prefix"],
                "type": "folder",
            })

        objects = []
        for obj in resp.get("Contents", []):
            key = obj["Key"]
            if key == prefix:
                continue
            name = key[len(prefix):]
            objects.append({
                "name": name,
                "key": key,
                "size": obj["Size"],
                "last_modified": obj["LastModified"].isoformat(),
                "storage_class": obj.get("StorageClass", "STANDARD"),
                "type": "file",
                "extension": name.rsplit(".", 1)[-1].lower() if "." in name else "",
            })

        return {
            "bucket": bucket,
            "prefix": prefix,
            "folders": folders,
            "objects": objects,
            "total": len(folders) + len(objects),
            "is_truncated": resp.get("IsTruncated", False),
            "next_token": resp.get("NextContinuationToken"),
            "error": None,
        }
    except ClientError as e:
        return {"folders": [], "objects": [], "error": str(e)}
    except Exception as e:
        return {"folders": [], "objects": [], "error": str(e)}


def get_object_info(bucket, key):
    """Get metadata for a single object (HEAD)."""
    try:
        s3 = get_client()
        resp = s3.head_object(Bucket=bucket, Key=key)
        return {
            "key": key,
            "size": resp["ContentLength"],
            "content_type": resp.get("ContentType", "application/octet-stream"),
            "last_modified": resp["LastModified"].isoformat(),
            "etag": resp.get("ETag", "").strip('"'),
            "metadata": dict(resp.get("Metadata", {})),
            "storage_class": resp.get("StorageClass", "STANDARD"),
            "error": None,
        }
    except ClientError as e:
        return {"error": str(e)}


def get_object_content(bucket, key, max_size=5 * 1024 * 1024):
    """Download object content for preview (max 5MB)."""
    try:
        s3 = get_client()

        # Check size first
        head = s3.head_object(Bucket=bucket, Key=key)
        size = head["ContentLength"]
        content_type = head.get("ContentType", "application/octet-stream")

        if size > max_size:
            return {
                "error": None,
                "too_large": True,
                "size": size,
                "content_type": content_type,
            }

        resp = s3.get_object(Bucket=bucket, Key=key)
        body = resp["Body"].read()

        return {
            "error": None,
            "too_large": False,
            "size": size,
            "content_type": content_type,
            "body": body,
        }
    except ClientError as e:
        return {"error": str(e)}


def generate_presigned_url(bucket, key, expires_in=3600):
    """Generate a presigned URL for direct download."""
    try:
        s3 = get_client()
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=expires_in,
        )
        return {"url": url, "error": None}
    except ClientError as e:
        return {"url": None, "error": str(e)}


def get_bucket_stats(bucket):
    """Quick stats: count a sample of objects."""
    try:
        s3 = get_client()
        resp = s3.list_objects_v2(Bucket=bucket, MaxKeys=1000)
        count = resp.get("KeyCount", 0)
        total_size = sum(o["Size"] for o in resp.get("Contents", []))
        is_truncated = resp.get("IsTruncated", False)
        return {
            "count": count,
            "total_size": total_size,
            "is_truncated": is_truncated,
            "error": None,
        }
    except ClientError as e:
        return {"error": str(e)}


# Cold storage classes (AWS + Scality)
COLD_CLASSES = {
    "GLACIER", "DEEP_ARCHIVE", "GLACIER_IR",
    "glacier-sc", "glacier-dc",
    "GLACIER-SC", "GLACIER-DC",
}


def is_cold_storage(storage_class: str) -> bool:
    return storage_class in COLD_CLASSES


def get_restore_status(bucket, key):
    """Check restore status via HEAD object x-amz-restore header."""
    try:
        s3 = get_client()
        resp = s3.head_object(Bucket=bucket, Key=key)
        restore_header = resp.get("Restore", "")
        storage_class = resp.get("StorageClass", "STANDARD")

        status = "available"
        if is_cold_storage(storage_class):
            if not restore_header:
                status = "frozen"
            elif 'ongoing-request="true"' in restore_header:
                status = "restoring"
            elif 'ongoing-request="false"' in restore_header:
                status = "restored"

        return {
            "storage_class": storage_class,
            "restore_header": restore_header,
            "status": status,
            "is_cold": is_cold_storage(storage_class),
            "error": None,
        }
    except ClientError as e:
        return {"error": str(e)}


def restore_object(bucket, key, days=7, tier="Standard"):
    """Request a restore from Glacier."""
    try:
        s3 = get_client()
        s3.restore_object(
            Bucket=bucket,
            Key=key,
            RestoreRequest={
                "Days": days,
                "GlacierJobParameters": {"Tier": tier},
            },
        )
        return {"status": "restore_initiated", "days": days, "tier": tier, "error": None}
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code == "RestoreAlreadyInProgress":
            return {"status": "already_restoring", "error": None}
        return {"error": str(e), "code": code}
    except Exception as e:
        return {"error": str(e)}


def get_bucket_lifecycle(bucket):
    """Get lifecycle configuration."""
    try:
        s3 = get_client()
        resp = s3.get_bucket_lifecycle_configuration(Bucket=bucket)
        rules = []
        for r in resp.get("Rules", []):
            rule = {
                "id": r.get("ID", "—"),
                "status": r.get("Status", "Unknown"),
                "prefix": r.get("Filter", {}).get("Prefix", r.get("Prefix", "*")),
            }
            transitions = []
            for t in r.get("Transitions", []):
                transitions.append({
                    "days": t.get("Days"),
                    "storage_class": t.get("StorageClass"),
                })
            rule["transitions"] = transitions

            if r.get("Expiration"):
                rule["expiration_days"] = r["Expiration"].get("Days")

            if r.get("NoncurrentVersionTransitions"):
                rule["noncurrent_transitions"] = [
                    {"days": t.get("NoncurrentDays"), "storage_class": t.get("StorageClass")}
                    for t in r["NoncurrentVersionTransitions"]
                ]

            if r.get("NoncurrentVersionExpiration"):
                rule["noncurrent_expiration_days"] = r["NoncurrentVersionExpiration"].get("NoncurrentDays")

            rules.append(rule)
        return {"rules": rules, "error": None}
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code == "NoSuchLifecycleConfiguration":
            return {"rules": [], "error": None}
        return {"rules": [], "error": str(e), "code": code}
    except Exception as e:
        return {"rules": [], "error": str(e)}


def get_bucket_policy(bucket):
    """Get bucket policy (JSON string)."""
    try:
        s3 = get_client()
        resp = s3.get_bucket_policy(Bucket=bucket)
        import json
        policy = json.loads(resp.get("Policy", "{}"))
        return {"policy": policy, "error": None}
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code == "NoSuchBucketPolicy":
            return {"policy": None, "error": None}
        return {"policy": None, "error": str(e), "code": code}
    except Exception as e:
        return {"policy": None, "error": str(e)}


def get_bucket_versioning(bucket):
    """Get versioning status."""
    try:
        s3 = get_client()
        resp = s3.get_bucket_versioning(Bucket=bucket)
        return {
            "status": resp.get("Status", "Disabled"),
            "mfa_delete": resp.get("MFADelete", "Disabled"),
            "error": None,
        }
    except ClientError as e:
        return {"error": str(e)}


def get_bucket_object_lock(bucket):
    """Get object lock configuration."""
    try:
        s3 = get_client()
        resp = s3.get_object_lock_configuration(Bucket=bucket)
        config = resp.get("ObjectLockConfiguration", {})
        rule = config.get("Rule", {}).get("DefaultRetention", {})
        return {
            "enabled": config.get("ObjectLockEnabled") == "Enabled",
            "mode": rule.get("Mode"),
            "days": rule.get("Days"),
            "years": rule.get("Years"),
            "error": None,
        }
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code in ("ObjectLockConfigurationNotFoundError", "NoSuchObjectLockConfiguration"):
            return {"enabled": False, "error": None}
        return {"enabled": False, "error": str(e), "code": code}
    except Exception as e:
        return {"enabled": False, "error": str(e)}


def get_bucket_tagging(bucket):
    """Get bucket tags."""
    try:
        s3 = get_client()
        resp = s3.get_bucket_tagging(Bucket=bucket)
        tags = {t["Key"]: t["Value"] for t in resp.get("TagSet", [])}
        return {"tags": tags, "error": None}
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code == "NoSuchTagSet":
            return {"tags": {}, "error": None}
        return {"tags": {}, "error": str(e), "code": code}
    except Exception as e:
        return {"tags": {}, "error": str(e)}