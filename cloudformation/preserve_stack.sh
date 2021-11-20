#!/bin/bash

# Copyright 2021 Chris Farris <chrisf@primeharbor.com>
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

STACK_NAME=$1

if [ -z "$STACK_NAME" ] ; then
	echo "USAGE: $0 <STACK_NAME>"
	exit 1
fi


DIR=${STACK_NAME}-PreservedStack
if [ ! -d $DIR ] ; then
	mkdir -p $DIR
fi

echo "Downloading Stack Parameters and Outputs to ${DIR}/StackStatus.json"
aws cloudformation describe-stacks --stack-name $STACK_NAME --output json > ${DIR}/StackStatus.json

echo "Downloading Stack Template to ${DIR}/Template.yaml"
aws cloudformation get-template --stack-name $STACK_NAME --query TemplateBody --output text > ${DIR}/Template.yaml