#!/usr/bin/env sh
set -eu

source_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
install_dir=${MARKET_SYSTEM_CONTRACTS_HOME:-"${XDG_DATA_HOME:-$HOME/.local/share}/market-system-contracts"}
mkdir -p "$install_dir"
cp -R "$source_dir/schemas" "$source_dir/docs" "$source_dir/testdata" "$install_dir/"
printf 'Market System Contracts installed in %s\n' "$install_dir"
