# Copyright The Cisco Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from collections import namedtuple

# DO NOT EDIT, this is an Auto-generated file from tools/templates/python/semantic_attributes.py.j2
class SemanticAttributes:
    DB_DYNAMO_PARAMETERS = "db.dynamo.parameters"
    """
    The request parameters.
    """

    DB_DYNAMO_RESPONSE = "db.dynamo.response"
    """
    The DynamoDB response data.
    """

    AWS_SNS_MESSAGE_ID = "aws.sns.message_id"
    """
    The message ID.
    """

    AWS_SNS_MESSAGE_STRUCTURE = "aws.sns.message_structure"
    """
    The message Message structure.
    """

    AWS_SNS_MESSAGE_ATTRIBUTE = "aws.sns.message_attribute"
    """
    A prefix for all message attributes collection.
    """

    AWS_SNS_PHONE_NUMBER = "aws.sns.phone_number"
    """
    The phone number for SMS sending.
    """

    AWS_SNS_TOPIC_ARN = "aws.sns.topic_arn"
    """
    The topic ARN ID.
    """

    AWS_SNS_SUBJECT = "aws.sns.subject"
    """
    The SNS subject.
    """

    AWS_SQS_QUEUE_NAME = "aws.sqs.queue_name"
    """
    The SQS queue name.
    Note: Assuming this structure for QueueUrl: https://sqs.<region>.amazonaws.com/<accountId>/<queueName>.
    """

    AWS_SQS_ACCOUNT_ID = "aws.sqs.account_id"
    """
    The user account id.
    Note: Assuming this structure for QueueUrl: https://sqs.<region>.amazonaws.com/<accountId>/<queueName>.
    """

    AWS_SQS_RECORD_MESSAGE_ID = "aws.sqs.record.message_id"
    """
    The record message ID.
    Note: Captured from SendMessage,ReceiveMessage only.
    """

    AWS_SQS_RECORD_MESSAGE_BODY = "aws.sqs.record.message_body"
    """
    The response body.
    Note: Captured from SendMessage,ReceiveMessage only.
    """

    AWS_SQS_RECORD_DELAY_SECONDS = "aws.sqs.record.delay_seconds"
    """
    The number in seconds to delay the message.
    """

    AWS_SQS_MESSAGE_ATTRIBUTE = "aws.sqs.message_attribute"
    """
    A prefix for all message attributes collection.
    """

    AWS_SQS_REQUEST_ENTRY = "aws.sqs.request_entry"
    """
    prefix to batch requets entries.
    """

    AWS_SQS_RESULT_ERROR_ENTRY = "aws.sqs.result_error_entry"
    """
    prefix to batch result error entries.
    """

    AWS_SQS_RESULT_ENTRY = "aws.sqs.result_entry"
    """
    prefix to batch result entries.
    """

    AWS_SQS_VISIBILITY_TIMEOUT = "aws.sqs.visibility_timeout"
    """
    The number in seconds of how long this message will be available to consume.
    """

    AWS_SQS_WAIT_TIME_SECONDS = "aws.sqs.wait_time_seconds"
    """
    The number in seconds for the polling time.
    """

    AWS_SQS_MAX_NUMBER_OF_MESSAGES = "aws.sqs.max_number_of_messages"
    """
    The maximum number of messages can recive.
    """

    AWS_SQS_ATTRIBUTE_NAME = "aws.sqs.attribute_name"
    """
    A prefix for all attributes names collection.
    """

    AWS_SQS_MESSAGE_ATTRIBUTE_NAME = "aws.sqs.message_attribute_name"
    """
    A prefix for all message attributes names collection.
    """

    AWS_SQS_RECORD_ATTRIBUTE = "aws.sqs.record.attribute"
    """
    prefix to record attributes.
    """

    AWS_SQS_RECORD_MESSAGE_ATTRIBUTE = "aws.sqs.record.message_attribute"
    """
    prefix to record message attributes.
    """

    AWS_SQS_AWS_SQS_RECORD = "aws.sqs.aws.sqs.record"
    """
    string list of all records.
    """

    RPC_REQUEST_METADATA = "rpc.request.metadata"
    """
    prefix to request metadata.
    """

    RPC_REQUEST_BODY = "rpc.request.body"
    """
    The transferred body.
    """

    RPC_RESPONSE_METADATA = "rpc.response.metadata"
    """
    prefix to response metadata.
    """

    RPC_RESPONSE_BODY = "rpc.response.body"
    """
    The transferred body.
    """

    HTTP_REQUEST_HEADER = "http.request.header"
    """
    HTTP request header. This describes the prefix to HTTP headers capturing.
    """

    HTTP_RESPONSE_HEADER = "http.response.header"
    """
    HTTP response header. This describes the prefix to HTTP headers capturing.
    """

    HTTP_REQUEST_BODY = "http.request.body"
    """
    HTTP message request body.
    """

    HTTP_RESPONSE_BODY = "http.response.body"
    """
    HTTP message response body.
    """

    MESSAGING_RABBITMQ_MESSAGE_HEADER = "messaging.rabbitmq.message.header"
    """
    prefix to headers.
    """

    MESSAGING_RABBITMQ_PAYLOAD = "messaging.rabbitmq.payload"
    """
    The transferred payload.
    """

    MESSAGING_RABBITMQ_PAYLOAD_SIZE = "messaging.rabbitmq.payload_size"
    """
    The transferred payload size in bytes.
    """

    DB_REDIS_ARGUMENTS = "db.redis.arguments"
    """
    The request arguments.
    """

    DB_REDIS_RESPONSE = "db.redis.response"
    """
    The response data.
    """
