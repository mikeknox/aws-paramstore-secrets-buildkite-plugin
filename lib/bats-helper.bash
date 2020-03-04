#!/bin/bash
set -eu

# shellcheck shell=bash

getAllEnvVarsAfterCmd() {
  # This is a helper function for testing
  "$@"
  local retVal=$?
  for var in $(compgen -v | grep -E '^(GIT|foo|bar)') ; do
    echo "${var}=${!var}"
  done
  # declare
  return $retVal
}
