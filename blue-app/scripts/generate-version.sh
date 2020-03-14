
pushd ../../
echo "$(git describe --abbrev=10)" > blue-app/scripts/version
popd
