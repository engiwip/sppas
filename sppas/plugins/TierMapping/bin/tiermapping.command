#!/bin/bash

dir=$( cd "$( dirname "$0" )" && pwd )
python "$dir"/tiermapping.pyw "$@"
